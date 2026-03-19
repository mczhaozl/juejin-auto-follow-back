
const set = new Set(['xiaochenlovecoding', 'mczhaozl', '被埋没的菜鸟', 'zengxiha', '古法编程纯手工', 'mczhaozl163', 'yalo970'])
[...document.querySelectorAll('.notification')].filter(el => set.has(el.querySelector('.name')?.innerText) || el.querySelector('.title')?.innerText?.includes?.('沸点')).forEach(el => el.style.display = 'none')