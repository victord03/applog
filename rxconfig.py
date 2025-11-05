import reflex as rx

config = rx.Config(
    app_name="applog",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)