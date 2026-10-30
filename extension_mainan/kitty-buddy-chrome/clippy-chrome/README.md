# Calico Kitten Buddy — for Google Chrome (and Chromium browsers)

A floating animated calico kitten character.

## Features
- Idle bounce animation when just sitting there
- **Drag & drop** — click and hold, then move it anywhere on the page
- **Click** it (without dragging) to get a random tip in English
- **Autonomous behavior** — when you leave it alone for a while, it will randomly:
  - 🚶 Walk left/right across the screen (faces the direction it's moving)
  - 🎉 Play (a little spin/hop)
  - 💤 Sleep (eyes close, "Zzz" appears)
  - ❤️ Show happiness (jumps a few times)

## Install on Google Chrome (or Edge / Brave / Opera)
1. Unzip this folder.
2. Open `chrome://extensions` in the address bar.
3. Turn on **Developer mode** (top-right toggle).
4. Click **Load unpacked** and select the unzipped `clippy-chrome` folder.
5. Open any website — Your kitten will appear in the bottom-right corner!

## Customize
- Edit the `TIPS` array in `content.js` to change what it says when clicked.
- Adjust timing in `activityLoop()` (`rand(6000, 13000)`) to make it more or less active.
- Edit `content.css` to change size, colors, or animation speed.
