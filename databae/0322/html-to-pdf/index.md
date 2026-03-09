# HTML 转 PDF 新方案：Puppeteer 的完美替代品

> 使用 jsPDF + html2canvas 或 Playwright 实现高质量 PDF 导出

---

## 一、方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| Puppeteer | 渲染完美 | 体积大、慢 |
| jsPDF | 轻量 | 样式支持差 |
| html2canvas | 前端实现 | 图片质量 |
| Playwright | 快速、稳定 | 需要环境 |

---

## 二、方案一：jsPDF + html2canvas

### 安装

```bash
npm install jspdf html2canvas
```

### 实现

```typescript
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

async function exportPDF(element: HTMLElement) {
  const canvas = await html2canvas(element, {
    scale: 2,  // 提高清晰度
    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO    useCO imgHeight = (canvas.height * imgWidth) / canvas.width;
  
  pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
  pdf.save('document.pdf');
}
```

---

## 三、方案二：Playwright

### 安装

```bash
npm install playwright
```

### 实现

```typescript
import { chromium } from 'playwright';

async function generatePDF(html: string) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.setContent(html);
  await page.pdf({
    path: 'document.pdf',
    format: 'A4',
    printBackground: true,
    margin: {
      top: '20mm',
      right: '20mm',
      bottom: '20mm',
      left: '20mm'
    }
  });
  
  await browser.close();
}
```

---

## 四、优化技巧

### 1. 分页处理

```css
@media print {
  .page-break {
    page-break-after: always;
  }
}
```

### 2. 样式优化

```css
@media print {
  body {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
```

---

## 总结

根据场景选择方案：
- 前端导出：jsPDF + html2canvas
- 服务端生成：Playwright
- 高质量要求：Playwright

如果这篇文章对你有帮助，欢迎点赞收藏！
