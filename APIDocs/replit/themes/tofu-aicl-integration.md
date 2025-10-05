# Themes API - tofu-aicl Integration

## Provider Resource
```hcl
data "replit_current_theme" "user_theme" {
  include_values = true
}

resource "openrouter_model" "theme_aware_ui" {
  model = "anthropic/claude-3.5-sonnet"

  prompt = templatefile("generate_ui.txt", {
    color_scheme = data.replit_current_theme.user_theme.color_scheme
    background_color = data.replit_current_theme.user_theme.values.background
    text_color = data.replit_current_theme.user_theme.values.foreground
    accent_color = data.replit_current_theme.user_theme.values.accent
  })
}
```

## Provider Implementation
```python
def ReadResource(self, request, context):
    if request.type_name == "replit_current_theme":
        theme_script = """
        import { themes } from '@replit/extensions';

        const [theme, values] = await Promise.all([
            themes.getCurrentTheme(),
            themes.getCurrentThemeValues()
        ]);

        return {
            name: theme.name,
            colorScheme: theme.colorScheme,
            values: {
                background: values.background,
                foreground: values.foreground,
                accent: values.accent,
                primary: values.primary,
                secondary: values.secondary
            }
        };
        """

        result = self._execute_in_replit(theme_script)

        state = provider_pb2.ResourceState(
            id="current-theme",
            type="replit_current_theme",
            status="active"
        )

        state.attributes.update({
            "name": result.get('name'),
            "color_scheme": result.get('colorScheme'),
            "background": result['values']['background'],
            "foreground": result['values']['foreground'],
            "accent": result['values']['accent']
        })

        return provider_pb2.ReadResourceResponse(state=state)
```

## Use Cases
- Generate UI components matching user's theme
- Create theme-aware documentation
- Build accessible color schemes for AI-generated interfaces
- Adapt AI-generated visualizations to user preferences