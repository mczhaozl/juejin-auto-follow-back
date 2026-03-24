# 如何开发一款 IDEA 插件：从 Demo 到实战

> 从零开始学习 IntelliJ IDEA 插件开发，包含环境搭建、核心概念、实战案例和优秀开源项目推荐。

---

## 目录 (Outline)
- [一、为什么要开发 IDEA 插件](#一为什么要开发-idea-插件)
- [二、环境搭建](#二环境搭建)
- [三、核心概念](#三核心概念)
- [四、实战案例 1：代码生成器](#四实战案例-1代码生成器)
- [五、实战案例 2：自定义 Inspection](#五实战案例-2自定义-inspection)
- [六、实战案例 3：工具窗口](#六实战案例-3工具窗口)
- [七、调试与测试](#七调试与测试)
- [八、发布插件](#八发布插件)
- [九、优秀开源项目推荐](#九优秀开源项目推荐)
- [十、学习资源](#十学习资源)
- [总结](#总结)

---

## 一、为什么要开发 IDEA 插件

### 常见场景

- 代码生成：根据模板生成代码
- 代码检查：自定义 Lint 规则
- 快捷操作：一键格式化、重构
- 工具集成：连接外部服务（数据库、API）
- 效率提升：自动化重复任务

### 优秀插件示例

- Lombok：自动生成 getter/setter
- MyBatis Plugin：XML 与 Mapper 跳转
- Translation：划词翻译
- Rainbow Brackets：彩虹括号
- GitToolBox：增强 Git 功能

## 二、环境搭建

### 1. 安装 IntelliJ IDEA

下载 IntelliJ IDEA Community Edition（免费）：
https://www.jetbrains.com/idea/download/

### 2. 安装 Plugin DevKit

IDEA 自带，无需额外安装。

### 3. 创建插件项目

```
File → New → Project → IDE Plugin
- Name: MyFirstPlugin
- Language: Java/Kotlin
- Build System: Gradle（推荐）
```

### 4. 项目结构

```
my-first-plugin/
├── src/
│   └── main/
│       ├── java/          # Java 代码
│       ├── kotlin/        # Kotlin 代码
│       └── resources/
│           ├── META-INF/
│           │   └── plugin.xml  # 插件配置
│           └── icons/     # 图标资源
├── build.gradle.kts       # Gradle 配置
└── gradle.properties
```

## 三、核心概念

### 1. plugin.xml 配置

```xml
<idea-plugin>
  <!-- 插件 ID，全局唯一 -->
  <id>com.example.myfirstplugin</id>
  
  <!-- 插件名称 -->
  <name>My First Plugin</name>
  
  <!-- 版本号 -->
  <version>1.0.0</version>
  
  <!-- 供应商信息 -->
  <vendor email="support@example.com" url="https://example.com">
    Example Company
  </vendor>
  
  <!-- 插件描述 -->
  <description><![CDATA[
    This is my first IDEA plugin.
  ]]></description>
  
  <!-- 兼容的 IDEA 版本 -->
  <idea-version since-build="221" until-build="233.*"/>
  
  <!-- 依赖的其他插件 -->
  <depends>com.intellij.modules.platform</depends>
  
  <!-- 扩展点 -->
  <extensions defaultExtensionNs="com.intellij">
    <!-- 在这里注册扩展 -->
  </extensions>
  
  <!-- 动作 -->
  <actions>
    <!-- 在这里注册动作 -->
  </actions>
</idea-plugin>
```

### 2. Action（动作）

Action 是用户可触发的操作（菜单项、工具栏按钮、快捷键）。

```java
public class HelloAction extends AnAction {
    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {
        // 获取项目
        Project project = e.getProject();
        
        // 显示通知
        NotificationGroupManager.getInstance()
            .getNotificationGroup("Custom Notification Group")
            .createNotification("Hello IDEA Plugin!", NotificationType.INFORMATION)
            .notify(project);
    }
}
```

在 plugin.xml 中注册：

```xml
<actions>
  <action id="MyPlugin.HelloAction" 
          class="com.example.HelloAction" 
          text="Say Hello"
          description="Show a hello message">
    <add-to-group group-id="ToolsMenu" anchor="first"/>
  </action>
</actions>
```

### 3. Extension（扩展）

Extension 用于扩展 IDEA 的功能。

```java
// 自定义文件类型
public class MyFileType extends LanguageFileType {
    public static final MyFileType INSTANCE = new MyFileType();
    
    private MyFileType() {
        super(MyLanguage.INSTANCE);
    }
    
    @Override
    public String getName() {
        return "My File";
    }
    
    @Override
    public String getDescription() {
        return "My custom file type";
    }
    
    @Override
    public String getDefaultExtension() {
        return "myext";
    }
    
    @Override
    public Icon getIcon() {
        return MyIcons.FILE;
    }
}
```

注册：

```xml
<extensions defaultExtensionNs="com.intellij">
  <fileType name="My File" 
            implementationClass="com.example.MyFileType" 
            fieldName="INSTANCE" 
            language="MyLanguage" 
            extensions="myext"/>
</extensions>
```

## 四、实战案例 1：代码生成器

### 需求

右键点击 Java 类，生成 Builder 模式代码。

### 实现

```java
public class GenerateBuilderAction extends AnAction {
    @Override
    public void actionPerformed(@NotNull AnActionEvent e) {
        // 获取当前编辑器和文件
        Editor editor = e.getData(CommonDataKeys.EDITOR);
        PsiFile psiFile = e.getData(CommonDataKeys.PSI_FILE);
        
        if (editor == null || psiFile == null) return;
        
        // 获取当前类
        PsiElement element = psiFile.findElementAt(editor.getCaretModel().getOffset());
        PsiClass psiClass = PsiTreeUtil.getParentOfType(element, PsiClass.class);
        
        if (psiClass == null) return;
        
        // 生成 Builder 类
        String builderCode = generateBuilderCode(psiClass);
        
        // 插入代码
        WriteCommandAction.runWriteCommandAction(e.getProject(), () -> {
            PsiElementFactory factory = JavaPsiFacade.getElementFactory(e.getProject());
            PsiClass builderClass = factory.createClassFromText(builderCode, psiClass);
            psiClass.add(builderClass);
        });
    }
    
    private String generateBuilderCode(PsiClass psiClass) {
        StringBuilder sb = new StringBuilder();
        sb.append("public static class Builder {\n");
        
        // 遍历字段
        for (PsiField field : psiClass.getFields()) {
            String fieldName = field.getName();
            String fieldType = field.getType().getPresentableText();
            
            sb.append("    private ").append(fieldType).append(" ").append(fieldName).append(";\n");
            sb.append("    public Builder ").append(fieldName).append("(").append(fieldType).append(" ").append(fieldName).append(") {\n");
            sb.append("        this.").append(fieldName).append(" = ").append(fieldName).append(";\n");
            sb.append("        return this;\n");
            sb.append("    }\n");
        }
        
        sb.append("    public ").append(psiClass.getName()).append(" build() {\n");
        sb.append("        return new ").append(psiClass.getName()).append("(this);\n");
        sb.append("    }\n");
        sb.append("}\n");
        
        return sb.toString();
    }
}
```

## 五、实战案例 2：自定义 Inspection

### 需求

检查代码中的魔法数字，提示用常量替代。

### 实现

```java
public class MagicNumberInspection extends LocalInspectionTool {
    @Override
    public PsiElementVisitor buildVisitor(@NotNull ProblemsHolder holder, boolean isOnTheFly) {
        return new JavaElementVisitor() {
            @Override
            public void visitLiteralExpression(PsiLiteralExpression expression) {
                super.visitLiteralExpression(expression);
                
                Object value = expression.getValue();
                if (value instanceof Integer || value instanceof Long) {
                    // 排除 0, 1, -1
                    if (value.equals(0) || value.equals(1) || value.equals(-1)) {
                        return;
                    }
                    
                    holder.registerProblem(
                        expression,
                        "Magic number detected, consider using a constant",
                        ProblemHighlightType.WEAK_WARNING,
                        new ReplaceWithConstantFix()
                    );
                }
            }
        };
    }
}
```

注册：

```xml
<extensions defaultExtensionNs="com.intellij">
  <localInspection language="JAVA"
                   displayName="Magic Number"
                   groupName="Code Quality"
                   enabledByDefault="true"
                   level="WARNING"
                   implementationClass="com.example.MagicNumberInspection"/>
</extensions>
```

## 六、实战案例 3：工具窗口

### 需求

创建一个工具窗口显示项目统计信息。

### 实现

```java
public class StatsToolWindowFactory implements ToolWindowFactory {
    @Override
    public void createToolWindowContent(@NotNull Project project, @NotNull ToolWindow toolWindow) {
        StatsToolWindow statsToolWindow = new StatsToolWindow(project);
        ContentFactory contentFactory = ContentFactory.SERVICE.getInstance();
        Content content = contentFactory.createContent(statsToolWindow.getContent(), "", false);
        toolWindow.getContentManager().addContent(content);
    }
}

public class StatsToolWindow {
    private JPanel contentPanel;
    private JLabel fileCountLabel;
    private JLabel lineCountLabel;
    
    public StatsToolWindow(Project project) {
        contentPanel = new JPanel();
        contentPanel.setLayout(new BoxLayout(contentPanel, BoxLayout.Y_AXIS));
        
        fileCountLabel = new JLabel("Files: 0");
        lineCountLabel = new JLabel("Lines: 0");
        
        contentPanel.add(fileCountLabel);
        contentPanel.add(lineCountLabel);
        
        // 计算统计信息
        calculateStats(project);
    }
    
    private void calculateStats(Project project) {
        // 遍历项目文件
        int fileCount = 0;
        int lineCount = 0;
        
        // ... 统计逻辑
        
        fileCountLabel.setText("Files: " + fileCount);
        lineCountLabel.setText("Lines: " + lineCount);
    }
    
    public JPanel getContent() {
        return contentPanel;
    }
}
```

注册：

```xml
<extensions defaultExtensionNs="com.intellij">
  <toolWindow id="Project Stats"
              anchor="right"
              factoryClass="com.example.StatsToolWindowFactory"/>
</extensions>
```

## 七、调试与测试

### 1. 运行插件

```
Run → Run 'Plugin'
```

会启动一个新的 IDEA 实例，插件已安装。

### 2. 调试

```
Run → Debug 'Plugin'
```

可以打断点调试。

### 3. 单元测试

```java
public class MyPluginTest extends LightJavaCodeInsightFixtureTestCase {
    @Override
    protected String getTestDataPath() {
        return "src/test/testData";
    }
    
    public void testAction() {
        myFixture.configureByText("Test.java", "public class Test {}");
        myFixture.testAction(new HelloAction());
        // 验证结果
    }
}
```

## 八、发布插件

### 1. 构建插件

```bash
./gradlew buildPlugin
```

生成的 zip 文件在 `build/distributions/`。

### 2. 发布到 JetBrains Marketplace

1. 注册账号：https://plugins.jetbrains.com/
2. 上传插件 zip
3. 填写描述、截图、变更日志
4. 提交审核

### 3. 版本管理

```kotlin
// build.gradle.kts
version = "1.0.1"

patchPluginXml {
    changeNotes.set("""
        <ul>
          <li>Fixed bug in code generation</li>
          <li>Added new inspection</li>
        </ul>
    """)
}
```

## 九、优秀开源项目推荐

### 1. Lombok Plugin
- GitHub: https://github.com/mplushnikov/lombok-intellij-plugin
- 学习：注解处理、代码生成

### 2. MyBatis Plugin
- GitHub: https://github.com/mybatis/mybatis-3
- 学习：XML 解析、跳转功能

### 3. Translation Plugin
- GitHub: https://github.com/YiiGuxing/TranslationPlugin
- 学习：HTTP 请求、UI 设计

### 4. Rainbow Brackets
- GitHub: https://github.com/izhangzhihao/intellij-rainbow-brackets
- 学习：语法高亮、颜色定制

### 5. GitToolBox
- GitHub: https://github.com/zielu/GitToolBox
- 学习：Git 集成、状态栏

## 十、学习资源

### 官方文档
- https://plugins.jetbrains.com/docs/intellij/

### 示例项目
- https://github.com/JetBrains/intellij-sdk-code-samples

### 社区
- JetBrains Platform Slack
- Stack Overflow: [intellij-plugin]

## 总结

开发 IDEA 插件的关键步骤：

1. 环境搭建：安装 IDEA + Plugin DevKit
2. 核心概念：Action、Extension、PSI
3. 实战练习：代码生成、Inspection、工具窗口
4. 调试测试：运行插件实例、单元测试
5. 发布分享：构建 zip、上传 Marketplace

推荐学习路径：

1. 从简单 Action 开始（Hello World）
2. 学习 PSI（代码结构分析）
3. 实现代码生成或检查
4. 添加 UI（工具窗口、对话框）
5. 参考优秀开源项目

开发插件能大幅提升团队效率，值得投入时间学习。
