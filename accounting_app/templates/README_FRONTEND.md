Frontend Upgrade Guide (Stable Stack)
- Goals: unify UI, remove external dependencies, enable offline assets, provide a small design system.
- Approach: Bootstrap 5 (local assets), CSS variables, simple design system, optional HTMX for progressive enhancements.
- Steps:
  1) Run npm install to pull bootstrap if desired; or use build:css script to compile SCSS to CSS.
  2) Run build:css to generate static/css/app.css from assets/scss.
  3) Link to /static/css/app.css in templates (preferably via a base template).
  4) Use macros for reusable form controls (to be added).
- Notes: This is a starting point; further refinement can include a small component library and a design system with tokens.
