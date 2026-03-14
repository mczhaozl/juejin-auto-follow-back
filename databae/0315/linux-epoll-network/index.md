# Linux 网络栈与 epoll：从网卡到用户态的高性能 I/O 模型剖析

> 从内核收包、协议栈、socket 到 epoll 的就绪通知与边缘触发，适合做服务端高并发与网络编程的深度参考。

---

## 一、为什么需要 epoll

传统 **select/poll** 的模型是：把一批 fd 交给内核，内核「轮询」这些 fd 是否就绪，再返回给用户态。问题在于：**fd 数量多时**，每次调用都要在用户态和内核态之间拷贝大量 fd 集合；**内核侧也是轮询**，O(n) 且无法利用硬件/驱动层的事件通知；**返回后用户态还要再遍历**才能知道「谁就绪」。在高并发、大量长连接的场景下，select/poll 成为瓶颈。**epoll** 把「监听的 fd 集合」常驻内核（**epoll_ctl 增删改**），通过 **epoll_wait** 只返回**当前就绪的 fd**，且内核用**事件驱动**（如网卡中断、套接字缓冲区可读）而非轮询，从而做到 **O(1)** 级别的就绪检测与 **O(就绪数)** 的返回，适合 C10K、C100K 级别的高并发服务。

## 二、从网卡到 socket：内核收包路径简述

数据包到达**网卡**后，由 **DMA** 写入内核的 **ring buffer（环形缓冲区）**，网卡触发**硬中断**；内核在中断上半部做最少工作（如标记 NAPI 轮询），然后**软中断**或 **ksoftirqd** 里做真正的**协议栈处理**：**L2 解包**、**L3 IP**、**L4 TCP/UDP**，根据四元组找到对应 **socket**，把数据放进该 socket 的 **接收缓冲区（receive buffer）**，并唤醒等待在该 socket 上的进程/线程。所以「数据就绪」的本质是：**socket 的 receive buffer 里有数据可读**（或 send buffer 有空间可写）。epoll 要监听的，就是这些 socket 的「可读/可写/异常」状态变化。

## 三、epoll 的三大 API

- **epoll_create / epoll_create1**：创建一个 **epoll 实例**，返回一个 fd（epfd）。内核会为该实例维护一棵 **红黑树**（存所有通过 epoll_ctl 添加的 fd）和一张**就绪链表（或就绪队列）**。
- **epoll_ctl(epfd, op, fd, event)**：**op** 为 **ADD/MOD/DEL**，向 epoll 实例**添加/修改/删除**要监听的 **fd** 及其关心的事件（**event**：如 EPOLLIN 可读、EPOLLOUT 可写、EPOLLET 边缘触发、EPOLLONESHOT 单次触发）。内核会把 fd 挂到内部结构上，并和网卡/协议栈的「就绪」事件挂钩。
- **epoll_wait(epfd, events[], maxevents, timeout)**：**阻塞**（或等待 timeout）直到有 fd 就绪，将就绪的 fd 及事件写入 **events** 数组，返回就绪数量。用户态只需遍历返回的少量 fd，无需再遍历全部监听的 fd。

## 四、边缘触发（ET）与水平触发（LT）

**水平触发（LT，默认）**：只要 fd 处于「可读/可写」状态，每次 **epoll_wait** 都会返回该 fd，直到用户把数据读完/写完。**边缘触发（ET）**：只在 fd 状态**从无到有变化**的那一瞬间通知一次；若用户一次没读完，下次 epoll_wait 不会再次通知，除非再有新数据到达。ET 能减少重复通知，但要求用户**一次读/写到 EAGAIN**，否则会漏事件。高并发场景下 ET + 非阻塞 fd 是常见组合，但代码复杂度更高；LT 更安全、易写。

## 五、epoll 与多路复用的本质

**多路复用**：用**一个（或少量）线程**监听**多个 fd**，谁就绪就处理谁，避免「一连接一线程」导致的上下文切换与内存开销。epoll 是 Linux 上实现多路复用的高效方案；与之对应的有 **kqueue**（BSD/macOS）、**IOCP**（Windows）。Nginx、Redis、Node.js 等的高并发能力，都依赖这类接口。理解「就绪」的含义（内核 buffer 有数据/有空间）、ET/LT 的差异、以及 **非阻塞 fd + 循环读写到 EAGAIN** 的写法，就能写出正确且高性能的网络服务。

## 六、常见坑与注意点

- **ET 下必须一次处理完**：读要用循环读到 EAGAIN，写同理，否则会丢事件或假死。
- **fd 务必设成非阻塞**：否则一次 read/write 可能阻塞整个事件循环。
- **epoll_ctl 的 event 要带 EPOLLIN/EPOLLOUT 等**：只关心读就只加 EPOLLIN，避免无谓的可写通知。
- **多线程共享 epfd**：可以，但 epoll_wait 的返回要由同一逻辑处理，或用 EPOLLEXCLUSIVE 等减少惊群。

## 七、总结

从**网卡 DMA → 内核协议栈 → socket 缓冲区**，到 **epoll 监听 socket 就绪 → epoll_wait 返回 → 用户态处理**，构成了 Linux 下高性能网络 I/O 的完整路径。epoll 通过「常驻监听集合 + 事件驱动 + 只返回就绪」避免了 select/poll 的 O(n) 与拷贝开销，是 C10K 及以上场景的标配。掌握 ET/LT、非阻塞与 EAGAIN 处理，即可在业务中正确使用 epoll。

## 八、延伸阅读

- 《UNIX 网络编程》第 6 章：I/O 复用与 epoll。
- Linux man：epoll_create、epoll_ctl、epoll_wait。
- 内核源码：`fs/eventpoll.c`（epoll 实现）。

## 九、实践：一个最小的 ET + 非阻塞 echo 骨架

用 **epoll_create1** 创建 epfd，**epoll_ctl(ADD)** 把 listen fd 加进去并设 **EPOLLIN | EPOLLET**；listen fd 设为 **O_NONBLOCK**。主循环里 **epoll_wait**，返回后遍历 events：若是 listen fd 则 **accept** 直到 EAGAIN，每个新连接 fd 也设非阻塞并 **epoll_ctl(ADD, EPOLLIN | EPOLLET)**；若是普通连接 fd 则 **read** 到 EAGAIN，把读到的数据写入写缓冲区，若可写则 **write** 到 EAGAIN。这样就是一个 ET + 非阻塞的典型骨架；实际项目里再叠加协议解析、超时、线程池等。通过这个小 demo 能巩固「就绪只通知一次」「必须读到 EAGAIN」的写法，避免 ET 下的常见坑。

---