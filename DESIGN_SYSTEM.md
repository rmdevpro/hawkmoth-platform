# HAWKMOTH Design System
*Professional Development Platform Design Standards*
*Updated: September 5, 2025*

## 🎯 Design Philosophy

**HAWKMOTH embodies precision, focus, and professional functionality.** The design system reflects the precision and adaptability of hawkmoths - clean, purposeful, and highly functional without unnecessary decoration.

### **Core Principles**
- **Functional over decorative** - Every element serves a specific purpose
- **Clean and minimal** - Focus on content and functionality
- **Professional appearance** - Suitable for enterprise development environments
- **Accessibility first** - Clear contrast, readable typography, semantic markup
- **Consistent patterns** - Predictable user experience across all interfaces

---

## 🎨 Color Palette

### **Primary Colors (Hawkmoth-Inspired)**
```css
--cicada-deep: #1a2f1a;      /* Deep forest green (primary dark) */
--cicada-dark: #2d4a2d;      /* Rich dark green (headers, emphasis) */
--cicada-medium: #4a6b4a;    /* Medium olive green (interactive elements) */
--cicada-sage: #6b8b6b;      /* Sage green (secondary text) */
--cicada-light: #8db18d;     /* Light green (buttons, accents) */
--cicada-mint: #b8d4b8;      /* Pale mint (subtle backgrounds) */
--cicada-whisper: #e8f4e8;   /* Very light green (borders, dividers) */
```

### **Functional Colors**
```css
--routing-blue: #2563eb;     /* LLM routing indicators */
--cost-amber: #d97706;       /* Cost tracking and warnings */
--success-green: #22c55e;    /* Success states, available status */
--warning-yellow: #f59e0b;   /* Warning states, configuration issues */
--error-red: #ef4444;        /* Error states, disconnected APIs */
```

### **Neutral Colors**
```css
--white: #ffffff;            /* Background, text on dark */
--black: #000000;            /* High contrast text when needed */
--gray-50: #f9fafb;          /* Light backgrounds */
--gray-900: #111827;         /* Dark text on light backgrounds */
```

---

## 📝 Typography

### **Font Stack**
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
```

**Rationale:** System fonts ensure native OS appearance, excellent performance, and accessibility across all platforms.

### **Font Weights**
- **400 (Regular):** Body text, standard content
- **500 (Medium):** Subheadings, emphasis within text
- **600 (Semi-bold):** Section headers, navigation items
- **700 (Bold):** Page titles, major headings

### **Font Sizes**
```css
--text-xs: 11px;    /* Helper text, metadata */
--text-sm: 12px;    /* Secondary content, labels */
--text-base: 14px;  /* Body text, primary content */
--text-lg: 16px;    /* Emphasized content */
--text-xl: 18px;    /* Section headers */
--text-2xl: 24px;   /* Page titles */
```

### **Line Heights**
- **Body text:** 1.6 (optimal for readability)
- **Headers:** 1.4 (tighter spacing for impact)
- **UI elements:** 1.2 (compact interface elements)

---

## 🎯 Icon Usage Guidelines

### **Functional Icons Only**
Icons are used **exclusively for functional purposes** - never as decoration.

#### **Approved Icon Uses:**
- **Status indicators:** ✅ ❌ ⚠️ (connection states, health checks)
- **Navigation arrows:** ▶ ▼ (expandable sections, dropdowns)
- **Action indicators:** 🔄 (loading, processing states)
- **Alert symbols:** 🚨 (critical warnings, errors)
- **Progress markers:** 📊 (analytics, completion states)

#### **Prohibited Icon Uses:**
- ❌ Decorative emojis in model names (🦅 🧠 💻)
- ❌ Aesthetic enhancement without function
- ❌ Brand decoration in headers or titles
- ❌ Emotional expression in professional interfaces

#### **Icon Standards:**
- **Size:** 12px-16px for inline, 20px-24px for standalone
- **Color:** Inherit from parent element or use functional colors
- **Accessibility:** Always include semantic meaning, not just visual

---

## 🎛️ Component Specifications

### **Headers and Navigation**
```css
/* Main header bar */
height: 50px;
background: linear-gradient(135deg, var(--cicada-dark) 0%, var(--cicada-deep) 100%);
color: white;
font-weight: 500;
font-size: 14px;
```

### **Status Indicators**
```css
/* Status dots */
width: 6px;
height: 6px;
border-radius: 50%;

/* Status colors */
.status-active { background: var(--success-green); }
.status-inactive { background: var(--error-red); }
.status-warning { background: var(--warning-yellow); }
```

### **Buttons**
```css
/* Primary button */
background: var(--cicada-light);
border-radius: 8px;
padding: 12px 16px;
font-weight: 500;
transition: background 0.2s;

/* Primary button hover */
background: var(--cicada-sage);
```

### **Input Fields**
```css
/* Text inputs */
border: 2px solid var(--cicada-whisper);
border-radius: 8px;
padding: 12px 16px;
font-size: 14px;

/* Focus state */
border-color: var(--cicada-light);
outline: none;
```

### **Cards and Containers**
```css
/* Content cards */
background: white;
border: 1px solid var(--cicada-whisper);
border-radius: 8px;
padding: 16px 20px;
```

---

## 🎨 Layout Standards

### **Spacing System**
```css
/* Base spacing unit: 4px */
--space-1: 4px;    /* Tight spacing */
--space-2: 8px;    /* Small gaps */
--space-3: 12px;   /* Medium gaps */
--space-4: 16px;   /* Standard spacing */
--space-5: 20px;   /* Large spacing */
--space-6: 24px;   /* Section spacing */
--space-8: 32px;   /* Major spacing */
--space-10: 40px;  /* Page-level spacing */
```

### **Container Widths**
- **Chat messages:** max-width: 800px (optimal reading width)
- **Sidebar:** width: 320px (sufficient for navigation)
- **Navigator:** width: 32px (minimal persistent presence)

### **Responsive Breakpoints**
```css
/* Mobile-first approach */
--mobile: 320px;     /* Small phones */
--tablet: 768px;     /* Tablets */
--desktop: 1024px;   /* Desktop */
--wide: 1280px;      /* Wide screens */
```

---

## 🎯 Interaction Patterns

### **Navigation**
- **Navigator bar:** Always visible, 32px width, click to expand sidebar
- **Sidebar:** Expandable to 320px, collapsible, contains project navigation
- **Breadcrumbs:** None required - simple hierarchy maintained in sidebar

### **State Management**
- **Loading states:** Subtle animation, clear progress indication
- **Error states:** Clear error messaging with corrective actions
- **Success states:** Confirmation without interrupting workflow

### **Content Organization**
- **Information hierarchy:** Clear visual hierarchy using typography and spacing
- **Scannable content:** Headers, bullet points, and white space for easy scanning
- **Progressive disclosure:** Complex information revealed as needed

---

## 🔧 Implementation Guidelines

### **CSS Architecture**
- **CSS Custom Properties:** Use for all colors, spacing, and repeated values
- **BEM Methodology:** Block__Element--Modifier naming convention
- **Progressive Enhancement:** Basic functionality works without JavaScript

### **Accessibility Standards**
- **WCAG 2.1 AA Compliance:** Minimum standard for all interfaces
- **Color Contrast:** 4.5:1 for normal text, 3:1 for large text
- **Keyboard Navigation:** All interactive elements keyboard accessible
- **Screen Readers:** Semantic HTML with appropriate ARIA labels

### **Performance Considerations**
- **System Fonts:** No custom font loading for optimal performance
- **Minimal CSS:** Only necessary styles, no framework overhead
- **Efficient Animations:** Use transform and opacity for smooth animations

---

## 🎨 Brand Application

### **Logo Usage**
- **HAWKMOTH wordmark:** Primary brand identifier
- **No icon-only branding:** Always include full platform name
- **Version indicators:** Clear version labeling (v0.1.0-dev)

### **Voice and Tone**
- **Professional:** Clear, direct, technical accuracy
- **Helpful:** Guidance without condescension  
- **Efficient:** Concise communication, respect for user time
- **Reliable:** Consistent terminology and behavior

---

## 📋 Design Review Checklist

Before implementing any interface changes:

- [ ] **Functional purpose:** Does every element serve a specific function?
- [ ] **Color compliance:** Are colors from the approved palette?
- [ ] **Typography:** System fonts with appropriate weights and sizes?
- [ ] **Icon usage:** Icons only for functional purposes, not decoration?
- [ ] **Accessibility:** Meets WCAG 2.1 AA standards?
- [ ] **Consistency:** Follows established patterns?
- [ ] **Performance:** Minimal impact on load times?
- [ ] **Responsive:** Works across all target devices?

---

## 🔄 Maintenance and Updates

### **Version Control**
- **Design System updates:** Document all changes with rationale
- **Component versioning:** Track component evolution
- **Breaking changes:** Clear migration guidance

### **Regular Reviews**
- **Quarterly assessment:** Evaluate design system effectiveness
- **User feedback integration:** Incorporate usability findings
- **Platform evolution:** Adapt to HAWKMOTH feature development

---

*HAWKMOTH Design System v1.0 - Precision, functionality, and professional excellence in every interface element.*
