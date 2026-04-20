# Rust Traits 完全指南

## 一、定义与实现 Trait

```rust
// 定义 Trait
trait Animal {
    fn make_sound(&self);
    
    // 默认实现
    fn sleep(&self) {
        println!("Zzz...");
    }
}

// 实现 Trait
struct Dog;
impl Animal for Dog {
    fn make_sound(&self) {
        println!("Woof!");
    }
}

struct Cat;
impl Animal for Cat {
    fn make_sound(&self) {
        println!("Meow!");
    }
}

fn main() {
    let dog = Dog;
    let cat = Cat;
    
    dog.make_sound();
    dog.sleep();
    
    cat.make_sound();
    cat.sleep();
}
```

## 二、Trait 作为参数

```rust
// 1. impl Trait 语法
fn make_animal_sound(animal: impl Animal) {
    animal.make_sound();
}

// 2. Trait Bound 语法
fn make_animal_sound<T: Animal>(animal: T) {
    animal.make_sound();
}

// 3. 多个 Trait
fn show<T: Animal + std::fmt::Display>(item: T) {
    println!("{}", item);
}
```

## 三、Trait 对象 (动态分发)

```rust
fn animal_sounds(animals: &[Box<dyn Animal>]) {
    for animal in animals {
        animal.make_sound();
    }
}

fn main() {
    let animals: Vec<Box<dyn Animal>> = vec![
        Box::new(Dog),
        Box::new(Cat),
    ];
    animal_sounds(&animals);
}
```

## 四、关联类型

```rust
trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}

struct Counter {
    count: u32,
}

impl Iterator for Counter {
    type Item = u32;
    fn next(&mut self) -> Option<Self::Item> {
        self.count += 1;
        if self.count < 6 {
            Some(self.count)
        } else {
            None
        }
    }
}
```

## 最佳实践
- 优先使用泛型 (静态分发)
- Trait 定义清晰的契约
- 使用默认实现减少重复
- 关联类型用于类型族
- 理解 Trait 对象的局限性
