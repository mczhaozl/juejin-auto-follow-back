# Rust 智能指针完全指南

## 一、Box<T>

```rust
fn main() {
    // 1. 堆上分配
    let b = Box::new(5);
    println!("b = {}", b);
    
    // 2. 递归类型
    enum List {
        Cons(i32, Box<List>),
        Nil,
    }
    
    let list = List::Cons(
        1, Box::new(List::Cons(2, Box::new(List::Nil)))
    );
}
```

## 二、Rc<T>

```rust
use std::rc::Rc;

fn main() {
    let a = Rc::new(5);
    println!("Count = {}", Rc::strong_count(&a));
    
    {
        let b = Rc::clone(&a);
        println!("Count = {}", Rc::strong_count(&a));
    }
    
    println!("Count = {}", Rc::strong_count(&a));
}
```

## 三、Arc<T>

```rust
use std::sync::Arc;
use std::thread;

fn main() {
    let a = Arc::new(5);
    let mut handles = vec![];
    
    for _ in 0..10 {
        let a = Arc::clone(&a);
        let handle = thread::spawn(move || {
            println!("{}", a);
        });
        handles.push(handle);
    }
    
    for h in handles {
        h.join().unwrap();
    }
}
```

## 四、RefCell<T>

```rust
use std::cell::RefCell;

fn main() {
    let data = RefCell::new(5);
    
    {
        let mut data_mut = data.borrow_mut();
        *data_mut += 1;
        println!("data = {}", data_mut);
    }
    
    let data_ref = data.borrow();
    println!("data = {}", data_ref);
}
```

## 最佳实践
- Box<T> 堆上单个所有者
- Rc<T> 单线程多个所有者
- Arc<T> 多线程多个所有者
- RefCell<T> 内部可变性（单线程）
- Mutex/RwLock 多线程内部可变性
