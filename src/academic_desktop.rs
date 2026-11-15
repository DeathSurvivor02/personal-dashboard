#![windows_subsystem = "windows"]

use tao::{
    dpi::LogicalSize,
    event::{Event, WindowEvent},
    event_loop::{ControlFlow, EventLoop},
    window::WindowBuilder,
};
use wry::WebViewBuilder;

fn main() -> wry::Result<()> {
    let event_loop = EventLoop::new();
    let window = WindowBuilder::new()
        .with_title("Official Academic Record & Gradebook — Centennial College")
        .with_inner_size(LogicalSize::new(1280.0, 820.0))
        .with_min_inner_size(LogicalSize::new(800.0, 600.0))
        .build(&event_loop)
        .expect("Failed to create desktop window");

    let _webview = WebViewBuilder::new(&window)
        .with_html(include_str!("../index.html"))
        .build()?;

    event_loop.run(move |event, _, control_flow| {
        *control_flow = ControlFlow::Wait;
        if let Event::WindowEvent {
            event: WindowEvent::CloseRequested,
            ..
        } = event
        {
            *control_flow = ControlFlow::Exit;
        }
    });
}
