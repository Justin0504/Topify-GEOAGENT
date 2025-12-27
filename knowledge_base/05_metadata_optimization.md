# Metadata and Structured Data Optimization

## Title and Description Best Practices

### Title Tag Optimization
- **Length**: 50-60 characters (optimal for display)
- **Format**: Include primary keyword near the beginning
- **Uniqueness**: Each page should have a unique title
- **Branding**: Include brand name if space allows
- **Readability**: Make it compelling and descriptive

### Meta Description Optimization
- **Length**: 150-160 characters (optimal for display)
- **Content**: Compelling summary that encourages clicks
- **Keywords**: Include primary keyword naturally
- **Call-to-Action**: Optional, but can improve CTR
- **Uniqueness**: Each page should have a unique description

## Open Graph Tags

### Essential OG Tags
- **og:title**: Page title (can differ from HTML title)
- **og:description**: Page description for social sharing
- **og:image**: Featured image (1200x630px recommended)
- **og:url**: Canonical URL of the page
- **og:type**: Content type (article, website, product, etc.)
- **og:site_name**: Site name

### Implementation
```html
<meta property="og:title" content="Page Title">
<meta property="og:description" content="Page description">
<meta property="og:image" content="https://example.com/image.jpg">
<meta property="og:url" content="https://example.com/page">
<meta property="og:type" content="article">
```

## Twitter Card Tags

### Twitter Card Types
- **summary**: Basic card with title, description, and image
- **summary_large_image**: Large image card
- **app**: Mobile app card
- **player**: Video/audio player card

### Essential Tags
- **twitter:card**: Card type
- **twitter:title**: Page title
- **twitter:description**: Page description
- **twitter:image**: Image URL
- **twitter:site**: Twitter username

## Schema.org Structured Data

### Common Schema Types

#### Article Schema
- **@type**: Article
- **headline**: Article title
- **description**: Article description
- **author**: Author information
- **datePublished**: Publication date
- **dateModified**: Last modified date
- **image**: Featured image

#### Organization Schema
- **@type**: Organization
- **name**: Organization name
- **url**: Website URL
- **logo**: Logo URL
- **contactPoint**: Contact information

#### FAQPage Schema
- **@type**: FAQPage
- **mainEntity**: Array of Question objects
- Each Question has **@type**: Question
- Each Question has **acceptedAnswer** with **@type**: Answer

#### BreadcrumbList Schema
- **@type**: BreadcrumbList
- **itemListElement**: Array of breadcrumb items
- Each item has **position**, **name**, and **item**

### JSON-LD Implementation
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "description": "Article description",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "datePublished": "2024-01-15",
  "dateModified": "2024-01-20"
}
```

## Metadata for AI Search Engines

### AI-Friendly Metadata
- **Clear Descriptions**: Help AI understand content purpose
- **Structured Information**: Use Schema.org for context
- **Comprehensive Coverage**: Include all relevant information
- **Question-Oriented**: Frame content around questions
- **Authority Signals**: Include author and publication info

### Best Practices
1. Write metadata for humans first, AI second
2. Include relevant keywords naturally
3. Provide comprehensive descriptions
4. Use structured data for context
5. Keep metadata updated with content
6. Test metadata with validation tools

## Validation Tools

### Recommended Tools
- Google Rich Results Test
- Schema.org Validator
- Facebook Sharing Debugger
- Twitter Card Validator
- LinkedIn Post Inspector

## Common Mistakes

1. **Duplicate Titles**: Using same title on multiple pages
2. **Missing Descriptions**: Not providing meta descriptions
3. **Incorrect Length**: Titles/descriptions too long or short
4. **No Structured Data**: Missing Schema.org markup
5. **Outdated Metadata**: Not updating when content changes
6. **Missing OG Tags**: No social media optimization

## Implementation Checklist

- [ ] Unique title tags (50-60 characters)
- [ ] Unique meta descriptions (150-160 characters)
- [ ] Open Graph tags implemented
- [ ] Twitter Card tags implemented
- [ ] Schema.org structured data added
- [ ] JSON-LD format used (recommended)
- [ ] Metadata validated with tools
- [ ] Social sharing tested
- [ ] Metadata updated regularly
- [ ] Mobile-friendly metadata

