from manim import *

class NavigationOrbit(Scene):
    """A gold voyage arc and arrowhead for the circumnavigation beat."""
    def construct(self):
        orbit=Circle(radius=2.0,stroke_color='#d8af69',stroke_width=2,stroke_opacity=.42)
        partial=Arc(radius=2.0,start_angle=PI*.75,angle=-PI*1.43,stroke_color='#f2d396',stroke_width=5)
        tip=Triangle(fill_color='#f4d99f',fill_opacity=1,stroke_width=0).scale(.10)
        tip.move_to(partial.get_end());tip.rotate(-PI*.70)
        self.add(orbit)
        self.play(Create(partial),run_time=2.3,rate_func=smooth)
        self.play(FadeIn(tip,scale=.6),run_time=.25)
        self.wait(.4)
