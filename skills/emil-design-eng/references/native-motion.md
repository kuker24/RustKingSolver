# Mobile Native & Touch Interaction Engineering

Engineering guidelines for mobile web polish and native mobile motion (React Native / Expo / iOS / Android). Synthesized from Emil Kowalski's mobile-native and animate-expo doctrines.

---

## 1. Web on Mobile: Eradicating Browser Tells

When running a web app on a mobile device, eliminating "website tells" transforms the perceived quality from an ordinary web page to an installed application:

### A. Viewport & 100dvh
- Standard `100vh` on mobile browsers includes the dynamic address bar, causing layout jumping when scrolling begins.
- Use `100dvh` (dynamic viewport height) or `100svh` (small viewport height) for full-screen application shells:
  ```css
  .app-shell {
    height: 100dvh;
    min-height: 100dvh;
  }
  ```
- Viewport meta tag configuration:
  ```html
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  ```

### B. Safe Area Insets (The Notch & Home Indicator)
Ensure fixed navigation bars, headers, and floating action buttons respect device safe zones:
```css
.header {
  padding-top: max(16px, env(safe-area-inset-top));
}
.bottom-bar {
  padding-bottom: max(16px, env(safe-area-inset-bottom));
}
```

### C. Eliminating the Gray Tap Highlight
Mobile Safari and Android Chrome flash an ugly gray rectangular highlight on tapped elements by default:
```css
* {
  -webkit-tap-highlight-color: transparent;
}
```

### D. Eliminating 300ms Tap Delay & Unwanted Pinch Zoom
Add `touch-action: manipulation` to interactive controls. This signals to the browser that double-tap-to-zoom is not needed, removing the 300ms gesture disambiguation delay:
```css
button, a, input, [role="button"] {
  touch-action: manipulation;
}
```

### E. Preventing iOS Auto-Zoom on Input Focus
iOS Safari automatically zooms the page when an `<input>`, `<select>`, or `<textarea>` has a font-size below 16px.
- Always set mobile input font size to at least `16px`:
  ```css
  input, select, textarea {
    font-size: 16px; /* Prevents viewport zoom */
  }
  ```

### F. Confining Overscroll on Sheets & Modals
Prevent pull-to-refresh or background body rubber-banding when scrolling a modal sheet:
```css
.sheet-scroll-container {
  overflow-y: auto;
  overscroll-behavior-y: contain;
  -webkit-overflow-scrolling: touch;
}
```

### G. Preventing Accidental Text Selection on Rapid Taps
Users double-tapping buttons or stepper controls should not trigger the blue native selection bubble:
```css
button, .clickable-badge, .nav-item {
  user-select: none;
  -webkit-user-select: none;
}
```

---

## 2. React Native & Expo Motion (Reanimated 3 & Gesture Handler)

When building for React Native and Expo, all fluid interaction logic runs on the UI thread via Reanimated worklets.

### A. The Core Rules of Reanimated
1. **Never drive animations on the JS thread.** Use `useSharedValue` and `useAnimatedStyle`.
2. **Worklets only**: Any function passed to gesture callbacks or `useAnimatedReaction` must run on the UI thread with the `'worklet';` directive.
3. **Springs with physical damping**: Avoid duration-based bezier timing for touch gestures.

### B. Pan Gesture with Velocity Handoff (Bottom Sheet Recipe)

```tsx
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  runOnJS,
} from 'react-native-reanimated';

export function BottomSheet({ onClose }: { onClose: () => void }) {
  const translateY = useSharedValue(0);

  const gesture = Gesture.Pan()
    .onChange((event) => {
      // 1:1 direct tracking downwards; damp upwards dragging
      if (event.translationY > 0) {
        translateY.value = event.translationY;
      } else {
        translateY.value = event.translationY * 0.2; // Rubber-band resistance
      }
    })
    .onEnd((event) => {
      // Velocity projection: if flicked down fast or dragged past 150px
      const shouldClose = event.translationY > 150 || event.velocityY > 600;

      if (shouldClose) {
        translateY.value = withSpring(
          600,
          { velocity: event.velocityY, damping: 25, stiffness: 250 },
          (finished) => {
            if (finished) runOnJS(onClose)();
          }
        );
      } else {
        // Snap back to open position
        translateY.value = withSpring(0, {
          velocity: event.velocityY,
          damping: 28,
          stiffness: 300,
        });
      }
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
  }));

  return (
    <GestureDetector gesture={gesture}>
      <Animated.View style={[styles.sheet, animatedStyle]}>
        {/* Sheet content */}
      </Animated.View>
    </GestureDetector>
  );
}
```

### C. Layout Animations for Lists
Use built-in layout transitions to smoothly animate item entry, deletion, and reordering without manual state coordination:

```tsx
import Animated, { FadeIn, FadeOut, LinearTransition } from 'react-native-reanimated';

<Animated.View
  entering={FadeIn.duration(200)}
  exiting={FadeOut.duration(160)}
  layout={LinearTransition.springify().damping(24).stiffness(280)}
>
  <ItemCard data={item} />
</Animated.View>
```

### D. Haptics Integration
Pair physical motion with tactile feedback (Expo Haptics / iOS Taptic Engine):
- **Light Selection**: On picker wheel turn or tab bar change (`Haptics.selectionAsync()`).
- **Impact Light**: On button release or toggle switch (`Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)`).
- **Notification Success**: On payment/task completion (`Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)`).
- **Never trigger heavy haptics on high-frequency typing or scroll events.**
