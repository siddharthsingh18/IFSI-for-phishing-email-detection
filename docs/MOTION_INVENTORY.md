# Motion inventory

The visual system intentionally limits motion to the interactions below. All
other decorative animation should be treated as a regression.

| Element | Trigger | Duration | Easing | Properties | Reduced motion |
| --- | --- | ---: | --- | --- | --- |
| Landing specimen UV beam | Pointer, touch, arrow keys | Continuous via `requestAnimationFrame` | Direct manipulation | Beam position only | Static revealed specimen |
| Landing hidden instructions | Keyboard Enter or reveal button | Instant | None | Visibility/color | Always visible |
| Page route transition | Route navigation | 200 ms | Settle | Opacity/translate | Disabled by Framer Motion preference |
| Landing scroll sequence A | Scroll into methods/key findings | 350–600 ms | Settle | Opacity/translate | Values remain visible |
| Instrument micro-interactions | Hover/focus/user action | 120–220 ms | Snap | Color/transform | Instant |
| Dot plot reveal | First visibility | Once | Settle | Opacity/scale | Immediate |
| Live-test lane scanning | Lane pending | Until completion | Linear loop | Transform | Paused/static |
| Live-test verdict stamp | Lane completion | 420 ms | Snap | Opacity/rotation/scale | Instant |

No ambient looping animation is part of the intended interaction model.
