const { chromium } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

(async () => {
  const targetDir = 'C:\\Users\\Max\\.gemini\\antigravity\\brain\\6c932651-2d27-44ac-8a59-0a6ba2b4c1e2';
  const darkPath = path.join(targetDir, 'timeline_topology_dark.png');
  const lightPath = path.join(targetDir, 'timeline_topology_light.png');

  console.log('Starting Playwright Chromium Browser...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  try {
    // 1. 访问 Timeline 页面
    console.log('Navigating to Timeline URL...');
    await page.goto('http://127.0.0.1:3000/timeline?workspace=demo-workspace', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // 额外等待一会儿确保 SVG 动画渲染和数据加载完毕
    await page.waitForTimeout(2000);

    // 2. 截取 Dark Mode
    console.log('Capturing Dark Mode topology...');
    await page.screenshot({ path: darkPath, fullPage: true });
    console.log(`Saved Dark Mode to: ${darkPath}`);

    // 3. 点击切换按钮
    console.log('Locating theme toggle button...');
    const themeBtn = page.locator('.theme-toggle');
    await themeBtn.click();
    console.log('Clicked theme toggle button!');

    // 等待 1.5s 以确保毛玻璃、背景渐变与 SVG 颜色顺利重绘渲染
    await page.waitForTimeout(1500);

    // 4. 截取 Light Mode
    console.log('Capturing Light Mode ("Crystal Aurora") topology...');
    await page.screenshot({ path: lightPath, fullPage: true });
    console.log(`Saved Light Mode to: ${lightPath}`);

  } catch (error) {
    console.error('E2E Screenshot Capture failed:', error);
  } finally {
    await browser.close();
    console.log('Browser closed. E2E visual verification sequence completed!');
  }
})();
