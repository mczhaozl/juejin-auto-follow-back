# Rust Yew 前端框架完全指南

## 一、Yew 基础

```toml
# Cargo.toml
[package]
name = "my-yew-app"
version = "0.1.0"
edition = "2021"

[dependencies]
yew = "0.21"
```

```rust
use yew::prelude::*;

#[function_component(App)]
fn app() -> Html {
    html! {
        <div class="container">
            <h1>{"Hello, Yew!"}</h1>
        </div>
    }
}

fn main() {
    yew::Renderer::<App>::new().render();
}
```

## 二、状态管理

```rust
use yew::prelude::*;

#[function_component(Counter)]
fn counter() -> Html {
    let count = use_state(|| 0);
    let onclick = {
        let count = count.clone();
        Callback::from(move |_| {
            count.set(*count + 1);
        })
    };

    html! {
        <div>
            <h2>{"Count: "}{*count}</h2>
            <button onclick={onclick}>{"Increment"}</button>
        </div>
    }
}
```

## 三、Props

```rust
use yew::prelude::*;

#[derive(PartialEq, Properties)]
struct Props {
    name: String,
}

#[function_component(Greeting)]
fn greeting(props: &Props) -> Html {
    html! {
        <div>
            <h2>{"Hello, "}{&props.name}</h2>
        </div>
    }
}

#[function_component(App)]
fn app() -> Html {
    html! {
        <Greeting name="Alice" />
    }
}
```

## 四、生命周期

```rust
use yew::prelude::*;

#[function_component(Lifecycle)]
fn lifecycle() -> Html {
    let data = use_state(|| None);
    
    use_effect_with_deps(
        move |_| {
            log::info!("Component mounted");
            
            || log::info!("Component unmounted")
        },
        (),
    );

    html! { <div>{"Lifecycle example"}</div> }
}
```

## 五、Context

```rust
use yew::prelude::*;
use yew::context::{ContextProvider, use_context};

#[derive(Clone, PartialEq)]
struct Theme {
    color: String,
}

#[function_component(ThemedButton)]
fn themed_button() -> Html {
    let theme = use_context::<Theme>();
    let color = theme.map(|t| t.color).unwrap_or("gray".to_string());

    html! {
        <button style={format!("background-color: {color}")}>
            {"Themed Button"}
        </button>
    }
}

#[function_component(App)]
fn app() -> Html {
    let theme = Theme { color: "blue".to_string() };

    html! {
        <ContextProvider<Theme> context={theme}>
            <ThemedButton />
        </ContextProvider<Theme>>
    }
}
```

## 六、事件处理

```rust
use yew::prelude::*;
use web_sys::HtmlInputElement;

#[function_component(Form)]
fn form() -> Html {
    let value = use_state(String::new);
    
    let oninput = {
        let value = value.clone();
        Callback::from(move |e: InputEvent| {
            let input: HtmlInputElement = e.target_unchecked_into();
            value.set(input.value());
        })
    };
    
    html! {
        <div>
            <input oninput={oninput} value={(*value).clone()} />
            <p>{"You wrote: "}{*value}</p>
        </div>
    }
}
```

## 七、最佳实践

- 使用函数组件而不是类组件
- 合理使用 use_state 和 use_reducer
- Context 用于全局状态
- 性能优化：减少不必要的渲染
- 测试组件逻辑
- 保持代码简洁和可读性
