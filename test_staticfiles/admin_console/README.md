# Admin Console Material Design Setup

## Overview

The Admin Console uses **Materialize CSS** as the Material Design framework. Materialize CSS is a modern responsive front-end framework based on Material Design principles.

## Framework Details

- **Framework**: Materialize CSS v1.0.0
- **Delivery Method**: CDN (Content Delivery Network)
- **Documentation**: https://materializecss.com/

## Files Structure

```
static/admin_console/
├── css/
│   └── admin_styles.css          # Custom styles with theme variables
├── js/
│   └── (JavaScript files to be added)
└── img/
    └── (Images to be added)
```

## CDN Resources

The following resources are loaded via CDN in the base template:

### CSS
- Materialize CSS: `https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css`
- Material Icons: `https://fonts.googleapis.com/icon?family=Material+Icons`

### JavaScript
- Materialize JS: `https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js`
- jQuery: `https://code.jquery.com/jquery-3.6.0.min.js`

## Theme Variables

The custom CSS file (`admin_styles.css`) defines CSS custom properties (variables) for theming:

### Light Mode (Default)
- Primary Color: `#1976d2` (Blue)
- Accent Color: `#ff9800` (Orange)
- Background: `#ffffff` (White)
- Text: `#212121` (Dark Gray)

### Dark Mode
- Background: `#1e1e1e` (Dark)
- Text: `#e0e0e0` (Light Gray)
- Sidebar: `#1a1a1a` (Darker)

## Theme Toggle

Users can switch between light and dark modes using the theme toggle button in the top navigation bar. The preference is saved in `localStorage` and persists across sessions.

## Material Design Components

The framework includes the following components:

### Layout
- Grid System (12-column responsive)
- Cards
- Collections
- Footer

### Forms
- Text Inputs
- Select Dropdowns
- Checkboxes
- Radio Buttons
- Switches
- File Inputs

### Navigation
- Navbar
- Sidenav (Sidebar)
- Breadcrumbs
- Pagination

### Components
- Buttons (Flat, Raised, Floating)
- Badges
- Chips
- Icons (Material Icons)
- Modals
- Tooltips
- Dropdowns
- Collapsible
- Tabs

### JavaScript
- Toasts (Notifications)
- Waves (Ripple Effect)
- Carousel
- Parallax
- Scrollspy

## Testing

To test the Material Design components:

1. Start the Django development server
2. Navigate to `/administration/test-components/`
3. Verify all components render correctly
4. Test theme toggle functionality
5. Test responsive behavior on different screen sizes

## Customization

To customize the theme:

1. Edit `static/admin_console/css/admin_styles.css`
2. Modify CSS custom properties in `:root` selector
3. Add custom styles as needed
4. Ensure dark mode compatibility by updating `body.dark-mode` selector

## Browser Support

Materialize CSS supports:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Opera (latest)

## Accessibility

Material Design components include:
- ARIA labels and roles
- Keyboard navigation support
- Focus indicators
- Screen reader compatibility

Ensure custom components maintain these accessibility features.

## Performance

Using CDN provides:
- Fast loading from geographically distributed servers
- Browser caching
- Reduced server load
- Automatic updates (when using `latest` version)

For production, consider:
- Downloading and hosting files locally
- Using specific version numbers instead of `latest`
- Minifying custom CSS
- Implementing a build process

## Next Steps

1. ✅ Install Materialize CSS via CDN
2. ✅ Create base template with sidebar layout
3. ✅ Set up theme variables for dark/light mode
4. ✅ Create test components page
5. 🔲 Implement dashboard with real data
6. 🔲 Create CRUD views for all modules
7. 🔲 Add JavaScript interactivity
8. 🔲 Implement authentication system
