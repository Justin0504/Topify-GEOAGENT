<script>
	import { marked } from 'marked';
	import { replaceTokens, processResponseContent } from '$lib/utils';
	import { user } from '$lib/stores';

	import markedExtension from '$lib/utils/marked/extension';
	import markedKatexExtension from '$lib/utils/marked/katex-extension';
	import { disableSingleTilde } from '$lib/utils/marked/strikethrough-extension';
	import { mentionExtension } from '$lib/utils/marked/mention-extension';

	import MarkdownTokens from './Markdown/MarkdownTokens.svelte';
	import footnoteExtension from '$lib/utils/marked/footnote-extension';
	import citationExtension from '$lib/utils/marked/citation-extension';

	export let id = '';
	export let content;
	export let done = true;
	export let model = null;
	export let save = false;
	export let preview = false;

	export let paragraphTag = 'p';
	export let editCodeBlock = true;
	export let topPadding = false;

	export let sourceIds = [];

	export let onSave = () => {};
	export let onUpdate = () => {};

	export let onPreview = () => {};

	export let onSourceClick = () => {};
	export let onTaskClick = () => {};

	let tokens = [];

	const options = {
		throwOnError: false,
		breaks: true
	};

	marked.use(markedKatexExtension(options));
	marked.use(markedExtension(options));
	marked.use(citationExtension(options));
	marked.use(footnoteExtension(options));
	marked.use(disableSingleTilde);
	marked.use({
		extensions: [mentionExtension({ triggerChar: '@' }), mentionExtension({ triggerChar: '#' })]
	});

	$: (async () => {
		if (content) {
			// 首先在原始内容中检测（最可能的位置）
			console.log('🔍 [Markdown] 开始检测 Calendar 导入数据，内容长度:', content.length);
			console.log('🔍 [Markdown] 内容预览:', content.substring(0, 200));
			
			const hasMarker = content.includes('CALENDAR_IMPORT_DATA');
			console.log('🔍 [Markdown] 是否包含 CALENDAR_IMPORT_DATA:', hasMarker);
			
			// 检测并提取 Calendar 导入数据（在内容处理之前）
			extractCalendarImportData(content);
			
			// 也检查处理后的内容（可能在转义后）
			const processedContent = replaceTokens(processResponseContent(content), model?.name, $user?.name);
			if (processedContent !== content) {
				console.log('🔍 [Markdown] 处理后的内容不同，再次检测');
				extractCalendarImportData(processedContent);
			}
			
			tokens = marked.lexer(processedContent);
		}
	})();

	// 从 content 中提取 Calendar 导入数据
	const extractCalendarImportData = (content) => {
		if (!content || typeof content !== 'string') return;
		
		try {
			// 查找 <!-- CALENDAR_IMPORT_DATA:... --> 标记（支持转义后的格式）
			const patterns = [
				/<!--\s*CALENDAR_IMPORT_DATA:([A-Za-z0-9+/=]+)\s*-->/,
				/&lt;!--\s*CALENDAR_IMPORT_DATA:([A-Za-z0-9+/=]+)\s*--&gt;/
			];
			
			let match = null;
			for (const regex of patterns) {
				match = content.match(regex);
				if (match && match[1]) break;
			}
			
			if (match && match[1]) {
				try {
					// 解码 base64
					const jsonStr = atob(match[1]);
					const data = JSON.parse(jsonStr);
					
					// 保存到 localStorage
					if (data && data.articles && Array.isArray(data.articles)) {
						localStorage.setItem('calendar_pending_import', JSON.stringify(data));
						console.log('✅ [Markdown] Calendar 导入数据已保存到 localStorage', data);
						console.log(`📊 [Markdown] 共 ${data.articles.length} 篇文章待导入`);
						
						// Trigger custom event to notify Calendar page if it's open
						window.dispatchEvent(new CustomEvent('calendar-import-ready', { detail: data }));
					}
				} catch (error) {
					console.error('解析 Calendar 导入数据失败:', error);
					console.error('Base64 字符串:', match[1].substring(0, 50) + '...');
				}
			} else {
				// Debug: check if the content contains the marker at all
				if (content.includes('CALENDAR_IMPORT_DATA')) {
					console.warn('⚠️ [Markdown] 检测到 CALENDAR_IMPORT_DATA 标记，但正则表达式未匹配');
					const idx = content.indexOf('CALENDAR_IMPORT_DATA');
					console.log('内容片段:', content.substring(Math.max(0, idx - 50), Math.min(content.length, idx + 200)));
				}
			}
		} catch (error) {
			console.error('提取 Calendar 导入数据失败:', error);
		}
	};
</script>

{#key id}
	<MarkdownTokens
		{tokens}
		{id}
		{done}
		{save}
		{preview}
		{paragraphTag}
		{editCodeBlock}
		{sourceIds}
		{topPadding}
		{onTaskClick}
		{onSourceClick}
		{onSave}
		{onUpdate}
		{onPreview}
	/>
{/key}
