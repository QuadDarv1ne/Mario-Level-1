"""Performance profiling and monitoring utilities."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any, Callable, Dict, Optional

import pygame as pg


class PerformanceTimer:
    """Measures execution time of code blocks."""
    
    def __init__(self, name: str) -> None:
        """Initialize performance timer.
        
        Args:
            name: Name of the timer for identification
        """
        self.name = name
        self.start_time: float = 0
        self.elapsed: float = 0
    
    def __enter__(self) -> PerformanceTimer:
        """Start timing."""
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args: Any) -> None:
        """Stop timing and calculate elapsed time."""
        self.elapsed = (time.perf_counter() - self.start_time) * 1000  # Convert to ms
    
    def get_elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds.
        
        Returns:
            Elapsed time in milliseconds
        """
        return self.elapsed


class PerformanceMonitor:
    """Monitors and tracks performance metrics over time."""
    
    def __init__(self, history_size: int = 60) -> None:
        """Initialize performance monitor.
        
        Args:
            history_size: Number of samples to keep in history
        """
        self.history_size = history_size
        self.timings: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.counters: Dict[str, int] = defaultdict(int)
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
    
    def record_timing(self, name: str, elapsed_ms: float) -> None:
        """Record timing measurement.
        
        Args:
            name: Name of the measurement
            elapsed_ms: Elapsed time in milliseconds
        """
        self.timings[name].append(elapsed_ms)
    
    def increment_counter(self, name: str, amount: int = 1) -> None:
        """Increment a counter.
        
        Args:
            name: Name of the counter
            amount: Amount to increment
        """
        self.counters[name] += amount
    
    def reset_counter(self, name: str) -> None:
        """Reset a counter to zero.
        
        Args:
            name: Name of the counter
        """
        self.counters[name] = 0
    
    def get_average(self, name: str) -> float:
        """Get average timing for a measurement.
        
        Args:
            name: Name of the measurement
            
        Returns:
            Average time in milliseconds
        """
        if name not in self.timings or not self.timings[name]:
            return 0.0
        return sum(self.timings[name]) / len(self.timings[name])
    
    def get_max(self, name: str) -> float:
        """Get maximum timing for a measurement.
        
        Args:
            name: Name of the measurement
            
        Returns:
            Maximum time in milliseconds
        """
        if name not in self.timings or not self.timings[name]:
            return 0.0
        return max(self.timings[name])
    
    def get_min(self, name: str) -> float:
        """Get minimum timing for a measurement.
        
        Args:
            name: Name of the measurement
            
        Returns:
            Minimum time in milliseconds
        """
        if name not in self.timings or not self.timings[name]:
            return 0.0
        return min(self.timings[name])
    
    def get_counter(self, name: str) -> int:
        """Get counter value.
        
        Args:
            name: Name of the counter
            
        Returns:
            Counter value
        """
        return self.counters.get(name, 0)
    
    def update_fps(self) -> None:
        """Update FPS calculation."""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def get_fps(self) -> int:
        """Get current FPS.
        
        Returns:
            Current FPS
        """
        return self.current_fps
    
    def get_report(self) -> str:
        """Generate performance report.
        
        Returns:
            Formatted performance report
        """
        lines = [
            "=== Performance Report ===",
            f"FPS: {self.current_fps}",
            "",
            "Timings (ms):",
        ]
        
        for name in sorted(self.timings.keys()):
            avg = self.get_average(name)
            min_val = self.get_min(name)
            max_val = self.get_max(name)
            lines.append(f"  {name}: avg={avg:.2f}, min={min_val:.2f}, max={max_val:.2f}")
        
        if self.counters:
            lines.append("")
            lines.append("Counters:")
            for name in sorted(self.counters.keys()):
                lines.append(f"  {name}: {self.counters[name]}")
        
        return "\n".join(lines)
    
    def clear(self) -> None:
        """Clear all measurements and counters."""
        self.timings.clear()
        self.counters.clear()
        self.frame_count = 0


class PerformanceOverlay:
    """Displays performance metrics on screen."""
    
    def __init__(self, monitor: PerformanceMonitor, font_size: int = 16) -> None:
        """Initialize performance overlay.
        
        Args:
            monitor: Performance monitor to display
            font_size: Font size for text
        """
        self.monitor = monitor
        self.font = pg.font.Font(None, font_size)
        self.visible = False
        self.background_color = (0, 0, 0, 180)
        self.text_color = (255, 255, 255)
        self.warning_color = (255, 255, 0)
        self.error_color = (255, 0, 0)
    
    def toggle(self) -> None:
        """Toggle overlay visibility."""
        self.visible = not self.visible
    
    def draw(self, surface: pg.Surface, x: int = 10, y: int = 10) -> None:
        """Draw performance overlay on surface.
        
        Args:
            surface: Surface to draw on
            x: X position
            y: Y position
        """
        if not self.visible:
            return
        
        lines = []
        
        # FPS
        fps = self.monitor.get_fps()
        fps_color = self.text_color
        if fps < 30:
            fps_color = self.error_color
        elif fps < 50:
            fps_color = self.warning_color
        
        lines.append((f"FPS: {fps}", fps_color))
        
        # Key timings
        key_metrics = [
            'frame_update',
            'collision_check',
            'sprite_update',
            'render',
        ]
        
        for metric in key_metrics:
            avg = self.monitor.get_average(metric)
            if avg > 0:
                color = self.text_color
                if avg > 16.67:  # Slower than 60 FPS
                    color = self.warning_color
                if avg > 33.33:  # Slower than 30 FPS
                    color = self.error_color
                
                lines.append((f"{metric}: {avg:.1f}ms", color))
        
        # Draw background
        line_height = self.font.get_height() + 2
        bg_height = len(lines) * line_height + 10
        bg_rect = pg.Rect(x - 5, y - 5, 200, bg_height)
        
        # Create semi-transparent surface
        bg_surface = pg.Surface((bg_rect.width, bg_rect.height), pg.SRCALPHA)
        bg_surface.fill(self.background_color)
        surface.blit(bg_surface, bg_rect.topleft)
        
        # Draw text
        current_y = y
        for text, color in lines:
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (x, current_y))
            current_y += line_height


def profile_function(func: Callable, monitor: PerformanceMonitor, name: Optional[str] = None) -> Callable:
    """Decorator to profile function execution time.
    
    Args:
        func: Function to profile
        monitor: Performance monitor to record to
        name: Optional name for the measurement (defaults to function name)
        
    Returns:
        Wrapped function
    """
    metric_name = name or func.__name__
    
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with PerformanceTimer(metric_name) as timer:
            result = func(*args, **kwargs)
        monitor.record_timing(metric_name, timer.get_elapsed_ms())
        return result
    
    return wrapper


# Global instance
_performance_monitor: Optional[PerformanceMonitor] = None
_performance_overlay: Optional[PerformanceOverlay] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance.
    
    Returns:
        Performance monitor instance
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_performance_overlay() -> PerformanceOverlay:
    """Get global performance overlay instance.
    
    Returns:
        Performance overlay instance
    """
    global _performance_overlay
    if _performance_overlay is None:
        monitor = get_performance_monitor()
        _performance_overlay = PerformanceOverlay(monitor)
    return _performance_overlay
