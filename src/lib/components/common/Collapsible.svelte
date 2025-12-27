<script lang="ts">
	import { decode } from 'html-entities';
	import { v4 as uuidv4 } from 'uuid';

	import { getContext } from 'svelte';
	const i18n = getContext('i18n');

	import dayjs from '$lib/dayjs';
	import duration from 'dayjs/plugin/duration';
	import relativeTime from 'dayjs/plugin/relativeTime';

	dayjs.extend(duration);
	dayjs.extend(relativeTime);

	async function loadLocale(locales) {
		if (!locales || !Array.isArray(locales)) {
			return;
		}
		for (const locale of locales) {
			try {
				dayjs.locale(locale);
				break; // Stop after successfully loading the first available locale
			} catch (error) {
				console.error(`Could not load locale '${locale}':`, error);
			}
		}
	}

	// Assuming $i18n.languages is an array of language codes
	$: loadLocale($i18n.languages);

	import { slide } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';

	import ChevronUp from '../icons/ChevronUp.svelte';
	import ChevronDown from '../icons/ChevronDown.svelte';
	import Spinner from './Spinner.svelte';
	import CodeBlock from '../chat/Messages/CodeBlock.svelte';
	import Markdown from '../chat/Messages/Markdown.svelte';
	import Image from './Image.svelte';
	import FullHeightIframe from './FullHeightIframe.svelte';
	import { settings } from '$lib/stores';

	export let open = false;

	export let className = '';
	export let buttonClassName =
		'w-fit text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition';

	export let id = '';
	export let title = null;
	export let attributes = null;
	
	// 强制工具调用结果始终折叠（不受用户设置影响）
	$: isToolCallType = attributes?.type === 'tool_calls';
	// 如果是工具调用类型，使用内部状态控制展开（默认折叠）
	// 非工具调用类型，使用传入的 open prop
	let toolCallOpen = false;
	$: effectiveOpen = isToolCallType ? toolCallOpen : open;

	export let chevron = false;
	export let grow = false;

	export let disabled = false;
	export let hide = false;

	export let onChange: Function = () => {};

	$: onChange(open);

	const collapsibleId = uuidv4();

	function parseJSONString(str) {
		try {
			return parseJSONString(JSON.parse(str));
		} catch (e) {
			return str;
		}
	}

	function formatJSONString(str) {
		if (!str) return '';
		try {
			let parsed = parseJSONString(str);
			
			// If the original string starts and ends with quotes, it's a JSON string
			// Try to extract the actual content
			const strTrimmed = String(str).trim();
			if (strTrimmed.startsWith('"') && strTrimmed.endsWith('"') && strTrimmed.length > 1) {
				try {
					// Try to parse as JSON string to extract the actual content
					parsed = JSON.parse(strTrimmed);
				} catch (e) {
					// If JSON parsing fails, try manual extraction
					const inner = strTrimmed.slice(1, -1);
					parsed = inner.replace(/\\n/g, '\n').replace(/\\t/g, '\t').replace(/\\r/g, '\r').replace(/\\"/g, '"');
				}
			}
			
			// If parsed is an object/array, then it's valid JSON
			if (typeof parsed === 'object' && parsed !== null) {
				return JSON.stringify(parsed, null, 2);
			} else {
				// It's a primitive value or string
				const strValue = String(parsed);
				// Replace escaped characters
				const normalized = strValue.replace(/\\n/g, '\n').replace(/\\t/g, '\t').replace(/\\r/g, '\r').replace(/\\"/g, '"');
				return normalized;
			}
		} catch (e) {
			// Not valid JSON, return as-is but handle newlines
			const strValue = String(str);
			const normalized = strValue.replace(/\\n/g, '\n').replace(/\\t/g, '\t').replace(/\\r/g, '\r').replace(/\\"/g, '"');
			return normalized;
		}
	}
	
	// Helper function to check if a string (possibly JSON-wrapped) contains Markdown
	function isMarkdownContent(str) {
		if (!str) return false;
		let content = String(str).trim();
		
		// If it's a JSON string, extract the inner content
		if (content.startsWith('"') && content.endsWith('"') && content.length > 1) {
			try {
				content = JSON.parse(content);
			} catch (e) {
				// Manual extraction
				content = content.slice(1, -1).replace(/\\n/g, '\n').replace(/\\"/g, '"');
			}
		}
		
		content = String(content);
		// Check for Markdown markers
		const hasMarkdownMarkers = content.includes('**') || content.includes('##') || content.includes('###') || 
		                           content.includes('📊') || content.includes('📄') || content.includes('💾') ||
		                           content.includes('─') || content.includes('═') || content.includes('│');
		// Check for newlines (multiline content that might be Markdown)
		const hasNewlines = content.includes('\n') || content.includes('\\n');
		
		return hasMarkdownMarkers || (hasNewlines && content.length > 100);
	}
</script>

<div {id} class={className}>
	{#if attributes?.type === 'tool_calls'}
		{@const args = decode(attributes?.arguments)}
		{@const result = decode(attributes?.result ?? '')}
		{@const files = parseJSONString(decode(attributes?.files ?? ''))}
		{@const embeds = parseJSONString(decode(attributes?.embeds ?? ''))}

		{#if embeds && Array.isArray(embeds) && embeds.length > 0}
			<div class="py-1 w-full cursor-pointer">
				<div class=" w-full text-xs text-gray-500">
					<div class="">
						{attributes.name}
					</div>
				</div>

				{#each embeds as embed, idx}
					<div class="my-2" id={`${collapsibleId}-tool-calls-${attributes?.id}-embed-${idx}`}>
						<FullHeightIframe
							src={embed}
							{args}
							allowScripts={true}
							allowForms={true}
							allowSameOrigin={true}
							allowPopups={true}
						/>
					</div>
				{/each}
			</div>
		{:else}
			<div
				class="{buttonClassName} cursor-pointer"
				on:pointerup={() => {
					if (!disabled) {
						if (isToolCallType) {
							toolCallOpen = !toolCallOpen;
						} else {
							open = !open;
						}
					}
				}}
			>
				<div
					class=" w-full font-medium flex items-center justify-between gap-2 {attributes?.done &&
					attributes?.done !== 'true'
						? 'shimmer'
						: ''}
			"
				>
					{#if attributes?.done && attributes?.done !== 'true'}
						<div>
							<Spinner className="size-4" />
						</div>
					{/if}

					<div class="">
						{#if attributes?.done === 'true'}
							<Markdown
								id={`${collapsibleId}-tool-calls-${attributes?.id}`}
								content={$i18n.t('View Result from **{{NAME}}**', {
									NAME: attributes.name
								})}
							/>
						{:else}
							<Markdown
								id={`${collapsibleId}-tool-calls-${attributes?.id}-executing`}
								content={$i18n.t('Executing **{{NAME}}**...', {
									NAME: attributes.name
								})}
							/>
						{/if}
					</div>

					<div class="flex self-center translate-y-[1px]">
						{#if effectiveOpen}
							<ChevronUp strokeWidth="3.5" className="size-3.5" />
						{:else}
							<ChevronDown strokeWidth="3.5" className="size-3.5" />
						{/if}
					</div>
				</div>
			</div>

			{#if !grow}
					{#if effectiveOpen && !hide}
					<div transition:slide={{ duration: 300, easing: quintOut, axis: 'y' }}>
						{#if attributes?.type === 'tool_calls'}
							<div class="text-xs max-h-96 overflow-auto p-2 bg-gray-50 dark:bg-gray-800 rounded">
								{#if attributes?.done === 'true'}
									{@const argsFormatted = formatJSONString(args)}
									{@const resultFormatted = formatJSONString(result)}
									{@const resultTrimmed = String(result || '').trim()}
									{@const isResultJSON = resultTrimmed.startsWith('{') || resultTrimmed.startsWith('[')}
									{@const isResultMarkdown = isMarkdownContent(resultTrimmed) && !isResultJSON}
									
									{#if isResultMarkdown}
										<!-- 如果结果是 Markdown 格式的字符串，直接渲染 -->
										<div class="mb-3">
											<div class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">Parameters:</div>
											<pre class="text-xs bg-white dark:bg-gray-900 p-2 rounded overflow-x-auto border border-gray-200 dark:border-gray-700"><code class="whitespace-pre-wrap">{argsFormatted}</code></pre>
										</div>
										<div>
											<div class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">Result:</div>
											<div class="bg-white dark:bg-gray-900 p-3 rounded border border-gray-200 dark:border-gray-700">
												<Markdown
													id={`${collapsibleId}-tool-calls-${attributes?.id}-result`}
													content={resultFormatted}
												/>
											</div>
										</div>
									{:else}
										<!-- 如果结果是 JSON，使用代码块显示 -->
										<Markdown
											id={`${collapsibleId}-tool-calls-${attributes?.id}-result`}
											content={`\`\`\`json
${argsFormatted}

${resultFormatted}
\`\`\``}
										/>
									{/if}
								{:else}
									<Markdown
										id={`${collapsibleId}-tool-calls-${attributes?.id}-result`}
										content={`\`\`\`json
${formatJSONString(args)}
\`\`\``}
									/>
								{/if}
							</div>
						{:else}
							<slot name="content" />
						{/if}
					</div>
				{/if}
			{/if}
		{/if}

		{#if attributes?.done === 'true'}
			{#if typeof files === 'object'}
				{#each files ?? [] as file, idx}
					{#if typeof file === 'string'}
						{#if file.startsWith('data:image/')}
							<Image
								id={`${collapsibleId}-tool-calls-${attributes?.id}-result-${idx}`}
								src={file}
								alt="Image"
							/>
						{/if}
					{:else if typeof file === 'object'}
						{#if file.type === 'image' && file.url}
							<Image
								id={`${collapsibleId}-tool-calls-${attributes?.id}-result-${idx}`}
								src={file.url}
								alt="Image"
							/>
						{/if}
					{/if}
				{/each}
			{/if}
		{/if}
	{:else}
		{#if title !== null}
			<!-- svelte-ignore a11y-no-static-element-interactions -->
			<!-- svelte-ignore a11y-click-events-have-key-events -->
			<div
				class="{buttonClassName} cursor-pointer"
				on:pointerup={() => {
					if (!disabled) {
						open = !open;
					}
				}}
			>
				<div
					class=" w-full font-medium flex items-center justify-between gap-2 {attributes?.done &&
					attributes?.done !== 'true'
						? 'shimmer'
						: ''}
			"
				>
					{#if attributes?.done && attributes?.done !== 'true'}
						<div>
							<Spinner className="size-4" />
						</div>
					{/if}

					<div class="">
						{#if attributes?.type === 'reasoning'}
							{#if attributes?.done === 'true' && attributes?.duration}
								{#if attributes.duration < 1}
									{$i18n.t('Thought for less than a second')}
								{:else if attributes.duration < 60}
									{$i18n.t('Thought for {{DURATION}} seconds', {
										DURATION: attributes.duration
									})}
								{:else}
									{$i18n.t('Thought for {{DURATION}}', {
										DURATION: dayjs.duration(attributes.duration, 'seconds').humanize()
									})}
								{/if}
							{:else}
								{$i18n.t('Thinking...')}
							{/if}
						{:else if attributes?.type === 'code_interpreter'}
							{#if attributes?.done === 'true'}
								{$i18n.t('Analyzed')}
							{:else}
								{$i18n.t('Analyzing...')}
							{/if}
						{:else}
							{title}
						{/if}
					</div>

					<div class="flex self-center translate-y-[1px]">
						{#if effectiveOpen}
							<ChevronUp strokeWidth="3.5" className="size-3.5" />
						{:else}
							<ChevronDown strokeWidth="3.5" className="size-3.5" />
						{/if}
					</div>
				</div>
			</div>
		{:else}
			<!-- svelte-ignore a11y-no-static-element-interactions -->
			<!-- svelte-ignore a11y-click-events-have-key-events -->
			<div
				class="{buttonClassName} cursor-pointer"
				on:click={(e) => {
					e.stopPropagation();
				}}
				on:pointerup={(e) => {
					if (!disabled) {
						open = !open;
					}
				}}
			>
				<div>
					<div class="flex items-start justify-between">
						<slot />

						{#if chevron}
							<div class="flex self-start translate-y-1">
								{#if effectiveOpen}
									<ChevronUp strokeWidth="3.5" className="size-3.5" />
								{:else}
									<ChevronDown strokeWidth="3.5" className="size-3.5" />
								{/if}
							</div>
						{/if}
					</div>

					{#if grow}
						{#if effectiveOpen && !hide}
							<div
								transition:slide={{ duration: 300, easing: quintOut, axis: 'y' }}
								on:pointerup={(e) => {
									e.stopPropagation();
								}}
							>
								<slot name="content" />
							</div>
						{/if}
					{/if}
				</div>
			</div>
		{/if}

		{#if !grow}
			{#if effectiveOpen && !hide}
				<div transition:slide={{ duration: 300, easing: quintOut, axis: 'y' }}>
					<slot name="content" />
				</div>
			{/if}
		{/if}
	{/if}
</div>
