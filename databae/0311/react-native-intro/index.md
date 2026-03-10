# React Native 完全入门：从原理到实战

> 一次编写，双端运行。带你从零理解 React Native 的工作原理，并手写一个简化版实现。

---

## 一、React Native 是什么

React Native（简称 RN）是 Facebook 开源的跨平台移动应用开发框架，让你用 JavaScript 和 React 语法编写原生 iOS 和 Android 应用。

核心特点：

- **真原生渲染**：不是 WebView，而是调用原生 UI 组件
- **热更新**：无需重新打包，线上修复 bug
- **跨平台**：一套代码，iOS 和 Android 共用 80%+ 逻辑
- **React 生态**：复用 React 的组件化、状态管理等能力

与其他方案对比：

| 方案 | 渲染方式 | 性能 | 开发体验 |
|------|---------|------|---------|
| 原生开发 | 原生 | 最优 | 需学 Swift/Kotlin |
| React Native | 原生 | 接近原生 | JavaScript + React |
| Flutter | 自绘引擎 | 接近原生 | Dart 语言 |
| Hybrid（Cordova） | WebView | 较差 | Web 技术栈 |

## 二、React Native 的工作原理

### 2.1 整体架构

```
┌─────────────────────────────────────┐
│      JavaScript 层（业务逻辑）       │
│      (React 组件、状态管理)          │
└──────────────┬──────────────────────┘
               │ Bridge（消息通信）
┌──────────────┴──────────────────────┐
│      Native 层（原生模块）           │
│      (UI 渲染、网络、存储等)         │
└─────────────────────────────────────┘
```

三层结构：

1. **JavaScript 层**：运行在 JavaScriptCore（iOS）或 Hermes（Android）引擎中，执行 React 代码
2. **Bridge**：JS 和 Native 之间的消息通道，传递 JSON 数据
3. **Native 层**：iOS 用 Objective-C/Swift，Android 用 Java/Kotlin，负责实际渲染和系统调用

### 2.2 渲染流程

```javascript
// 1. 你写的 JSX
<View style={{ flex: 1 }}>
  <Text>Hello RN</Text>
</View>

// 2. React 转成虚拟 DOM
{
  type: 'View',
  props: { style: { flex: 1 } },
  children: [
    { type: 'Text', props: {}, children: ['Hello RN'] }
  ]
}

// 3. Bridge 传给 Native
{
  "type": "createView",
  "viewId": 1,
  "viewType": "RCTView",
  "props": { "flex": 1 }
}

// 4. Native 创建真实 UI
UIView *view = [[UIView alloc] init];  // iOS
// 或
View view = new View(context);         // Android
```

### 2.3 Bridge 通信

JS 调用 Native：

```javascript
// JS 端
import { NativeModules } from 'react-native';
const { ToastModule } = NativeModules;

ToastModule.show('Hello', ToastModule.SHORT);
```

Native 实现（iOS）：

```objective-c
// ToastModule.m
#import <React/RCTBridgeModule.h>

@interface ToastModule : NSObject <RCTBridgeModule>
@end

@implementation ToastModule

RCT_EXPORT_MODULE();

RCT_EXPORT_METHOD(show:(NSString *)message duration:(NSInteger)duration) {
  dispatch_async(dispatch_get_main_queue(), ^{
    // 显示 Toast
  });
}

@end
```

Native 调用 JS：

```objective-c
// Native 端
[self.bridge enqueueJSCall:@"RCTDeviceEventEmitter"
                    method:@"emit"
                      args:@[@"onNetworkChange", @{@"type": @"wifi"}]
                completion:NULL];
```

```javascript
// JS 端
import { NativeEventEmitter, NativeModules } from 'react-native';

const eventEmitter = new NativeEventEmitter(NativeModules.ToastModule);
eventEmitter.addListener('onNetworkChange', (event) => {
  console.log('网络变化:', event.type);
});
```

## 三、从零搭建 React Native 项目

### 3.1 环境准备

安装依赖：

```bash
# macOS（开发 iOS 需要）
brew install node watchman
sudo gem install cocoapods

# 安装 React Native CLI
npm install -g react-native-cli
```

安装 Xcode（iOS）或 Android Studio（Android）。

### 3.2 创建项目

```bash
npx react-native init MyApp
cd MyApp
```

目录结构：

```
MyApp/
├── android/          # Android 原生代码
├── ios/              # iOS 原生代码
├── node_modules/
├── App.tsx           # 入口组件
├── index.js          # 注册入口
├── package.json
└── metro.config.js   # 打包配置
```

### 3.3 运行项目

```bash
# iOS
npx react-native run-ios

# Android（需先启动模拟器或连接真机）
npx react-native run-android
```

## 四、核心组件

### 4.1 View 和 Text

```javascript
import { View, Text, StyleSheet } from 'react-native';

function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Hello React Native</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333'
  }
});
```

### 4.2 Image

```javascript
<Image
  source={{ uri: 'https://example.com/image.png' }}
  style={{ width: 200, height: 200 }}
  resizeMode="cover"
/>

// 本地图片
<Image source={require('./assets/logo.png')} />
```

### 4.3 ScrollView 和 FlatList

```javascript
// ScrollView：适合少量数据
<ScrollView>
  {data.map(item => <Text key={item.id}>{item.name}</Text>)}
</ScrollView>

// FlatList：适合长列表，支持虚拟滚动
<FlatList
  data={data}
  keyExtractor={item => item.id}
  renderItem={({ item }) => <Text>{item.name}</Text>}
  onEndReached={loadMore}
  onEndReachedThreshold={0.5}
/>
```

### 4.4 TouchableOpacity

```javascript
<TouchableOpacity
  onPress={() => console.log('点击')}
  activeOpacity={0.7}
>
  <Text>点我</Text>
</TouchableOpacity>
```

## 五、样式与布局

### 5.1 Flexbox 布局

RN 默认使用 Flexbox，但有些差异：

```javascript
// 默认 flexDirection 是 column（Web 是 row）
<View style={{ flexDirection: 'row' }}>
  <View style={{ flex: 1, backgroundColor: 'red' }} />
  <View style={{ flex: 2, backgroundColor: 'blue' }} />
</View>
```

### 5.2 尺寸单位

RN 没有 `px`、`rem`，只有无单位数字（对应设备独立像素 dp/pt）：

```javascript
<View style={{ width: 100, height: 50 }} />
```

### 5.3 响应式布局

```javascript
import { Dimensions } from 'react-native';

const { width, height } = Dimensions.get('window');

<View style={{ width: width * 0.8 }} />
```

## 六、手写简化版 React Native

### 6.1 核心思路

1. 解析 JSX 生成虚拟 DOM
2. 遍历虚拟 DOM，生成 Native 指令
3. 通过 Bridge 发送给 Native
4. Native 创建真实 UI

### 6.2 虚拟 DOM 转指令

```javascript
function renderToNative(vdom, parentId = 0) {
  const viewId = generateId();
  const instructions = [];

  // 创建视图指令
  instructions.push({
    type: 'createView',
    viewId,
    viewType: vdom.type,  // 'View', 'Text' 等
    parentId,
    props: vdom.props
  });

  // 递归处理子节点
  if (vdom.children) {
    vdom.children.forEach(child => {
      if (typeof child === 'string') {
        // 文本节点
        instructions.push({
          type: 'updateText',
          viewId,
          text: child
        });
      } else {
        instructions.push(...renderToNative(child, viewId));
      }
    });
  }

  return instructions;
}
```

### 6.3 Bridge 实现

```javascript
class Bridge {
  constructor() {
    this.queue = [];
  }

  // JS 调用 Native
  callNative(module, method, args) {
    this.queue.push({ module, method, args });
    this.flush();
  }

  // 批量发送
  flush() {
    if (this.queue.length === 0) return;

    const batch = this.queue.splice(0);
    // 实际会调用 Native 的 C++ 接口
    window.__nativeBridge.processBatch(JSON.stringify(batch));
  }

  // Native 调用 JS
  invokeCallback(callbackId, args) {
    const callback = this.callbacks[callbackId];
    if (callback) callback(...args);
  }
}
```

### 6.4 Native 端处理（伪代码）

```swift
// iOS 端
class NativeBridge {
  func processBatch(_ json: String) {
    let batch = JSON.parse(json)
    
    for instruction in batch {
      switch instruction.type {
      case "createView":
        let view = createView(instruction.viewType)
        view.tag = instruction.viewId
        applyProps(view, instruction.props)
        parentView.addSubview(view)
        
      case "updateText":
        let label = viewRegistry[instruction.viewId] as! UILabel
        label.text = instruction.text
      }
    }
  }
}
```

### 6.5 完整示例

```javascript
// 1. JSX
const App = () => (
  <View style={{ flex: 1 }}>
    <Text>Hello</Text>
  </View>
);

// 2. 转虚拟 DOM
const vdom = {
  type: 'View',
  props: { style: { flex: 1 } },
  children: [
    { type: 'Text', props: {}, children: ['Hello'] }
  ]
};

// 3. 生成指令
const instructions = renderToNative(vdom);
// [
//   { type: 'createView', viewId: 1, viewType: 'View', props: {...} },
//   { type: 'createView', viewId: 2, viewType: 'Text', parentId: 1 },
//   { type: 'updateText', viewId: 2, text: 'Hello' }
// ]

// 4. 发送给 Native
bridge.callNative('UIManager', 'createView', instructions);
```

## 七、常用库与生态

### 7.1 导航

```bash
npm install @react-navigation/native @react-navigation/stack
```

```javascript
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

const Stack = createStackNavigator();

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Detail" component={DetailScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### 7.2 状态管理

```bash
npm install zustand
```

```javascript
import create from 'zustand';

const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 }))
}));

function Counter() {
  const { count, increment } = useStore();
  return <Text onPress={increment}>{count}</Text>;
}
```

### 7.3 网络请求

```javascript
fetch('https://api.example.com/data')
  .then(res => res.json())
  .then(data => console.log(data));

// 或使用 axios
import axios from 'axios';
const { data } = await axios.get('/api/data');
```

## 八、性能优化

### 8.1 避免不必要的渲染

```javascript
import { memo } from 'react';

const ListItem = memo(({ item }) => (
  <Text>{item.name}</Text>
));
```

### 8.2 使用 FlatList 而非 ScrollView

```javascript
// ❌ 差
<ScrollView>
  {data.map(item => <Item key={item.id} />)}
</ScrollView>

// ✅ 好
<FlatList
  data={data}
  renderItem={({ item }) => <Item item={item} />}
/>
```

### 8.3 图片优化

```javascript
<Image
  source={{ uri: url }}
  style={{ width: 200, height: 200 }}
  resizeMode="cover"
  // 启用缓存
  cache="force-cache"
/>
```

## 九、调试技巧

### 9.1 开发者菜单

模拟器中按 `Cmd + D`（iOS）或 `Cmd + M`（Android）打开菜单，可以：

- Reload：重新加载
- Debug：打开 Chrome DevTools
- Show Inspector：查看元素

### 9.2 日志

```javascript
console.log('普通日志');
console.warn('警告');
console.error('错误');
```

### 9.3 Flipper

Facebook 官方调试工具，支持网络、布局、日志等：

```bash
brew install flipper
```

## 十、打包发布

### 10.1 iOS

```bash
# 1. 打开 Xcode
open ios/MyApp.xcworkspace

# 2. 选择 Generic iOS Device
# 3. Product -> Archive
# 4. 上传到 App Store Connect
```

### 10.2 Android

```bash
# 1. 生成签名密钥
keytool -genkey -v -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000

# 2. 配置 android/gradle.properties
MYAPP_RELEASE_STORE_FILE=my-release-key.keystore
MYAPP_RELEASE_KEY_ALIAS=my-key-alias
MYAPP_RELEASE_STORE_PASSWORD=***
MYAPP_RELEASE_KEY_PASSWORD=***

# 3. 打包
cd android
./gradlew assembleRelease

# 4. APK 在 android/app/build/outputs/apk/release/
```

## 总结

React Native 让你用 JavaScript 写原生应用，核心原理：

- JS 层运行 React 代码，生成虚拟 DOM
- Bridge 传递 JSON 指令给 Native
- Native 层创建真实 UI 组件

关键要点：

- 使用 View、Text、Image 等基础组件
- Flexbox 布局，默认 `flexDirection: column`
- FlatList 处理长列表
- React Navigation 做路由
- 通过 NativeModules 调用原生能力

适合快速开发跨平台应用，性能接近原生。
