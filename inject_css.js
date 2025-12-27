// Open WebUI 工具显示修复脚本
// 在浏览器控制台（Console）中运行此脚本

(function() {
  // 创建 style 标签
  const style = document.createElement('style');
  style.id = 'open-webui-tool-fix';
  style.textContent = `
    /* 修复工具结果显示的换行和样式 */
    details[type="tool_calls"] pre,
    details[type="tool_calls"] code,
    [id*="tool-calls"] pre,
    [id*="tool-calls"] code {
      white-space: pre-wrap !important;
      word-wrap: break-word !important;
      font-size: 11px !important;
      line-height: 1.6 !important;
    }
    
    details[type="tool_calls"] pre code {
      white-space: pre-wrap !important;
      white-space: -moz-pre-wrap !important;
      white-space: -pre-wrap !important;
      white-space: -o-pre-wrap !important;
    }
    
    details[type="tool_calls"] .prose,
    [id*="tool-calls-result"] .prose {
      white-space: pre-wrap !important;
      max-height: 400px !important;
      overflow-y: auto !important;
    }
    
    details[type="tool_calls"] [class*="markdown"] {
      white-space: pre-wrap !important;
    }
    
    details[type="tool_calls"] p,
    details[type="tool_calls"] div {
      white-space: pre-wrap !important;
    }
    
    details[type="tool_calls"] {
      font-size: 12px !important;
    }
    
    details[type="tool_calls"] .bg-gray-50,
    details[type="tool_calls"] .bg-gray-800 {
      padding: 12px !important;
      border-radius: 6px !important;
    }
    
    /* 改善 JSON 显示 */
    details[type="tool_calls"] pre {
      background: #f9fafb !important;
      padding: 12px !important;
      border-radius: 6px !important;
      border: 1px solid #e5e7eb !important;
    }
    
    [data-theme="dark"] details[type="tool_calls"] pre {
      background: #1f2937 !important;
      border-color: #374151 !important;
    }
  `;
  
  // 注入到页面
  if (!document.getElementById('open-webui-tool-fix')) {
    document.head.appendChild(style);
    console.log('✅ Open WebUI 工具显示修复已应用');
  } else {
    console.log('⚠️  修复脚本已存在');
  }
})();

