# Rust Traits 完全指南

## 一、定义 Trait

```rust
trait Animal {
    fn make_sound(&self);
}

struct Dog;
impl Animal for Dog {
    fn make_sound(&self) {
        println!("Woof");
    }
}
```

## 二、默认方法

```rust
trait Greeter {
    fn greet(&self) {
        println!("Hello");
    }
}

struct Person;
impl Greeter for Person {}
```

## 三、泛型约束

```rust
fn print_sound<T: Animal>(a: T) {
    a.make_sound();
}

fn print_sound_impl(a: impl Animal) {
    a.make_sound();
}
```

## 四、Trait Object

```rust
trait Animal { fn make_sound(&self); }

struct Cat; impl Animal for Cat { fn make_sound(&self) { println!("Meow"); } }

fn main() {
    let animals: Vec<Box<dyn Animal>> = vec![
        Box::new(Dog),
        Box::new(Cat),
    ];
    
    for a in animals {
        a.make_sound();
    }
}
```

## 最佳实践
- Trait 抽象行为
- 合理设计 Trait 粒度
- 默认方法复用
- 约束 vs Trait Object
- 使用标准库 Trait
