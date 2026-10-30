(function () {
  "use strict";

  if (document.getElementById("clippy-buddy-root")) return;

  var TIPS = [
    "Hi there! Looks like you're browsing. Need a hand?",
    "Tip: Press Ctrl+T (or Cmd+T on Mac) to open a new tab.",
    "You can drag me anywhere on the screen!",
    "Tip: Ctrl+Shift+T reopens the last tab you closed.",
    "Remember to save your work often!",
    "Tip: You can zoom a page with Ctrl and + or -.",
    "Feeling stuck? Take a short break and stretch a little.",
    "Tip: Ctrl+F lets you search for text on this page.",
    "I'm just a friendly calico kitten, here to keep you company. Meow!",
    "Tip: Bookmark this page with Ctrl+D if you want to find it again.",
    "Great job getting things done today!",
    "Tip: Middle-click a link to open it in a new tab.",
    "I like to wander around and nap when you're not looking!"
  ];

  function rand(min, max) { return Math.random() * (max - min) + min; }
  function randInt(min, max) { return Math.floor(rand(min, max + 1)); }
  function randomTip() { return TIPS[randInt(0, TIPS.length - 1)]; }
  function wait(ms) { return new Promise(function (res) { setTimeout(res, ms); }); }

  // ---- Build DOM ----
  var root = document.createElement("div");
  root.id = "clippy-buddy-root";

  var status = document.createElement("div");
  status.id = "clippy-buddy-status";

  var bubble = document.createElement("div");
  bubble.id = "clippy-buddy-bubble";

  var bubbleText = document.createElement("span");
  bubbleText.id = "clippy-buddy-bubble-text";
  bubble.appendChild(bubbleText);

  var closeBtn = document.createElement("div");
  closeBtn.id = "clippy-buddy-close";
  closeBtn.textContent = "\u00D7";
  bubble.appendChild(closeBtn);

  var character = document.createElement("div");
  character.id = "clippy-buddy-character";
  character.setAttribute("role", "button");
  character.setAttribute("aria-label", "Calico Kitten Buddy, draggable");

  var flip = document.createElement("div");
  flip.id = "clippy-buddy-flip";
  flip.innerHTML = `<svg viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"><defs><clipPath id="cb-head-clip"><circle cx="50" cy="44" r="26"/></clipPath><clipPath id="cb-body-clip"><ellipse cx="50" cy="84.3" rx="24.7" ry="23.4"/></clipPath><clipPath id="cb-tail-clip"><circle cx="63.59" cy="97.17" r="5.72"/><circle cx="65.89" cy="97.56" r="5.62"/><circle cx="68.05" cy="97.72" r="5.52"/><circle cx="70.05" cy="97.68" r="5.41"/><circle cx="71.91" cy="97.45" r="5.31"/><circle cx="73.62" cy="97.03" r="5.21"/><circle cx="75.19" cy="96.45" r="5.11"/><circle cx="76.61" cy="95.71" r="5"/><circle cx="77.89" cy="94.82" r="4.9"/><circle cx="79.02" cy="93.81" r="4.8"/><circle cx="80.01" cy="92.68" r="4.7"/><circle cx="80.86" cy="91.44" r="4.6"/><circle cx="81.57" cy="90.11" r="4.49"/><circle cx="82.14" cy="88.7" r="4.39"/><circle cx="82.57" cy="87.23" r="4.29"/><circle cx="82.87" cy="85.7" r="4.19"/><circle cx="83.03" cy="84.13" r="4.09"/><circle cx="83.05" cy="82.53" r="3.98"/><circle cx="82.94" cy="80.91" r="3.88"/><circle cx="82.7" cy="79.3" r="3.78"/><circle cx="82.33" cy="77.69" r="3.68"/><circle cx="81.82" cy="76.11" r="3.58"/><circle cx="81.19" cy="74.56" r="3.47"/><circle cx="80.42" cy="73.06" r="3.37"/><circle cx="79.53" cy="71.63" r="3.27"/><circle cx="78.51" cy="70.27" r="3.17"/><circle cx="77.36" cy="68.99" r="3.06"/><circle cx="76.09" cy="67.81" r="2.96"/><circle cx="74.7" cy="66.75" r="2.86"/></clipPath></defs><g><circle cx="63.59" cy="97.17" r="7.02" fill="#28201a"/><circle cx="65.89" cy="97.56" r="6.92" fill="#28201a"/><circle cx="68.05" cy="97.72" r="6.82" fill="#28201a"/><circle cx="70.05" cy="97.68" r="6.71" fill="#28201a"/><circle cx="71.91" cy="97.45" r="6.61" fill="#28201a"/><circle cx="73.62" cy="97.03" r="6.51" fill="#28201a"/><circle cx="75.19" cy="96.45" r="6.41" fill="#28201a"/><circle cx="76.61" cy="95.71" r="6.3" fill="#28201a"/><circle cx="77.89" cy="94.82" r="6.2" fill="#28201a"/><circle cx="79.02" cy="93.81" r="6.1" fill="#28201a"/><circle cx="80.01" cy="92.68" r="6" fill="#28201a"/><circle cx="80.86" cy="91.44" r="5.9" fill="#28201a"/><circle cx="81.57" cy="90.11" r="5.79" fill="#28201a"/><circle cx="82.14" cy="88.7" r="5.69" fill="#28201a"/><circle cx="82.57" cy="87.23" r="5.59" fill="#28201a"/><circle cx="82.87" cy="85.7" r="5.49" fill="#28201a"/><circle cx="83.03" cy="84.13" r="5.39" fill="#28201a"/><circle cx="83.05" cy="82.53" r="5.28" fill="#28201a"/><circle cx="82.94" cy="80.91" r="5.18" fill="#28201a"/><circle cx="82.7" cy="79.3" r="5.08" fill="#28201a"/><circle cx="82.33" cy="77.69" r="4.98" fill="#28201a"/><circle cx="81.82" cy="76.11" r="4.88" fill="#28201a"/><circle cx="81.19" cy="74.56" r="4.77" fill="#28201a"/><circle cx="80.42" cy="73.06" r="4.67" fill="#28201a"/><circle cx="79.53" cy="71.63" r="4.57" fill="#28201a"/><circle cx="78.51" cy="70.27" r="4.47" fill="#28201a"/><circle cx="77.36" cy="68.99" r="4.36" fill="#28201a"/><circle cx="76.09" cy="67.81" r="4.26" fill="#28201a"/><circle cx="74.7" cy="66.75" r="4.16" fill="#28201a"/><circle cx="63.59" cy="97.17" r="5.72" fill="#fdf3e6"/><circle cx="65.89" cy="97.56" r="5.62" fill="#fdf3e6"/><circle cx="68.05" cy="97.72" r="5.52" fill="#fdf3e6"/><circle cx="70.05" cy="97.68" r="5.41" fill="#fdf3e6"/><circle cx="71.91" cy="97.45" r="5.31" fill="#fdf3e6"/><circle cx="73.62" cy="97.03" r="5.21" fill="#fdf3e6"/><circle cx="75.19" cy="96.45" r="5.11" fill="#fdf3e6"/><circle cx="76.61" cy="95.71" r="5" fill="#fdf3e6"/><circle cx="77.89" cy="94.82" r="4.9" fill="#fdf3e6"/><circle cx="79.02" cy="93.81" r="4.8" fill="#fdf3e6"/><circle cx="80.01" cy="92.68" r="4.7" fill="#fdf3e6"/><circle cx="80.86" cy="91.44" r="4.6" fill="#fdf3e6"/><circle cx="81.57" cy="90.11" r="4.49" fill="#fdf3e6"/><circle cx="82.14" cy="88.7" r="4.39" fill="#fdf3e6"/><circle cx="82.57" cy="87.23" r="4.29" fill="#fdf3e6"/><circle cx="82.87" cy="85.7" r="4.19" fill="#fdf3e6"/><circle cx="83.03" cy="84.13" r="4.09" fill="#fdf3e6"/><circle cx="83.05" cy="82.53" r="3.98" fill="#fdf3e6"/><circle cx="82.94" cy="80.91" r="3.88" fill="#fdf3e6"/><circle cx="82.7" cy="79.3" r="3.78" fill="#fdf3e6"/><circle cx="82.33" cy="77.69" r="3.68" fill="#fdf3e6"/><circle cx="81.82" cy="76.11" r="3.58" fill="#fdf3e6"/><circle cx="81.19" cy="74.56" r="3.47" fill="#fdf3e6"/><circle cx="80.42" cy="73.06" r="3.37" fill="#fdf3e6"/><circle cx="79.53" cy="71.63" r="3.27" fill="#fdf3e6"/><circle cx="78.51" cy="70.27" r="3.17" fill="#fdf3e6"/><circle cx="77.36" cy="68.99" r="3.06" fill="#fdf3e6"/><circle cx="76.09" cy="67.81" r="2.96" fill="#fdf3e6"/><circle cx="74.7" cy="66.75" r="2.86" fill="#fdf3e6"/></g><g clip-path="url(#cb-tail-clip)"><ellipse cx="75.94" cy="83.13" rx="9.88" ry="9.36" fill="#28201a"/><ellipse cx="71" cy="98.34" rx="8.64" ry="8.19" fill="#e89444"/></g><ellipse cx="50" cy="84.3" rx="24.7" ry="23.4" fill="#fdf3e6" stroke="#28201a" stroke-width="2.6"/><g clip-path="url(#cb-body-clip)"><ellipse cx="62.84" cy="77.28" rx="10.87" ry="10.53" fill="#e89444"/><ellipse cx="37.16" cy="96" rx="10.87" ry="10.76" fill="#28201a"/></g><ellipse cx="50" cy="84.3" rx="24.7" ry="23.4" fill="none" stroke="#28201a" stroke-width="2.6"/><ellipse cx="33.88" cy="99.51" rx="7.8" ry="6.24" fill="#28201a" stroke="#28201a" stroke-width="2.6"/><path d="M 33.88 93.27 A 7.8 6.24 0 0 1 33.88 105.75 Z" fill="#fdf3e6" stroke="#28201a" stroke-width="2.6"/><ellipse cx="51.3" cy="99.51" rx="7.8" ry="6.24" fill="#fdf3e6" stroke="#28201a" stroke-width="2.6"/><polygon points="21.4,36.2 30.5,6.3 44.8,32.3" fill="#fdf3e6" stroke="#28201a" stroke-width="2.6" stroke-linejoin="round"/><polygon points="26.08,32.3 30.5,14.62 38.3,31.52" fill="#f7a9c0"/><polygon points="78.6,36.2 69.5,6.3 55.2,32.3" fill="#28201a" stroke="#28201a" stroke-width="2.6" stroke-linejoin="round"/><polygon points="73.92,32.3 69.5,14.62 61.7,31.52" fill="#f7a9c0"/><circle cx="50" cy="44" r="26" fill="#fdf3e6" stroke="#28201a" stroke-width="2.6"/><g clip-path="url(#cb-head-clip)"><ellipse cx="37.78" cy="31.39" rx="11.7" ry="12.09" fill="#e89444"/><ellipse cx="64.17" cy="39.32" rx="10.53" ry="8.84" fill="#28201a"/></g><circle cx="50" cy="44" r="26" fill="none" stroke="#28201a" stroke-width="2.6"/><circle id="clippy-buddy-eye-left" cx="37" cy="47.12" r="4.29" fill="#28201a"/><circle id="clippy-buddy-eye-right" cx="63" cy="47.12" r="4.29" fill="#28201a"/><circle cx="35.5" cy="45.4" r="1.43" fill="#fff"/><circle cx="61.5" cy="45.4" r="1.43" fill="#fff"/><ellipse cx="32.71" cy="59.6" rx="5.59" ry="3.9" fill="#f6aec0" opacity="0.75"/><ellipse cx="67.29" cy="59.6" rx="5.59" ry="3.9" fill="#f6aec0" opacity="0.75"/><polygon points="47.92,56.48 52.08,56.48 50,59.6" fill="#f7a9c0"/><path d="M 41.68 55.44 Q 45.58 62.72 49.48 60.12" fill="none" stroke="#28201a" stroke-width="1.17" stroke-linecap="round"/><path d="M 50.52 60.12 Q 54.42 62.72 58.32 55.44" fill="none" stroke="#28201a" stroke-width="1.17" stroke-linecap="round"/><line x1="22.7" y1="49.2" x2="1.9" y2="47.64" stroke="#28201a" stroke-width="0.7" stroke-linecap="round"/><line x1="77.3" y1="49.2" x2="98.1" y2="47.64" stroke="#28201a" stroke-width="0.7" stroke-linecap="round"/><line x1="22.7" y1="51.8" x2="1.9" y2="50.24" stroke="#28201a" stroke-width="0.7" stroke-linecap="round"/><line x1="77.3" y1="51.8" x2="98.1" y2="50.24" stroke="#28201a" stroke-width="0.7" stroke-linecap="round"/><line x1="22.7" y1="54.4" x2="1.9" y2="52.84" stroke="#28201a" stroke-width="0.7" stroke-linecap="round"/><line x1="77.3" y1="54.4" x2="98.1" y2="52.84" stroke="#28201a" stroke-width="0.7" stroke-linecap="round"/></svg>`;

  character.appendChild(flip);
  root.appendChild(status);
  root.appendChild(bubble);
  root.appendChild(character);
  document.documentElement.appendChild(root);

  // ---- Initial position (bottom-right corner) ----
  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

  function initPosition() {
    var w = root.offsetWidth || 72;
    var h = root.offsetHeight || 84;
    var left = window.innerWidth - w - 24;
    var top = window.innerHeight - h - 24;
    root.style.left = clamp(left, 0, window.innerWidth - w) + "px";
    root.style.top = clamp(top, 0, window.innerHeight - h) + "px";
  }
  initPosition();

  window.addEventListener("resize", function () {
    var rect = root.getBoundingClientRect();
    root.style.left = clamp(rect.left, 0, window.innerWidth - rect.width) + "px";
    root.style.top = clamp(rect.top, 0, window.innerHeight - rect.height) + "px";
  });

  // ---- Speech bubble (click tips) ----
  var hideTimer = null;
  function showBubble(text) {
    bubbleText.textContent = text;
    bubble.classList.add("visible");
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(function () { bubble.classList.remove("visible"); }, 5000);
  }

  closeBtn.addEventListener("pointerdown", function (e) { e.stopPropagation(); });
  closeBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    bubble.classList.remove("visible");
    if (hideTimer) clearTimeout(hideTimer);
  });

  // ---- Status emoji (ambient activities) ----
  var statusTimer = null;
  function showStatus(emoji, duration) {
    status.textContent = emoji;
    status.classList.add("visible");
    if (statusTimer) clearTimeout(statusTimer);
    if (duration) {
      statusTimer = setTimeout(function () { status.classList.remove("visible"); }, duration);
    }
  }
  function hideStatus() {
    status.classList.remove("visible");
  }

  // ---- Drag & drop ----
  var isDragging = false;
  var dragMoved = false;
  var offsetX = 0, offsetY = 0, startPX = 0, startPY = 0;
  var lastInteraction = 0;

  character.addEventListener("pointerdown", function (e) {
    isDragging = true;
    dragMoved = false;
    lastInteraction = Date.now();
    var rect = root.getBoundingClientRect();
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;
    startPX = e.clientX;
    startPY = e.clientY;
    root.style.transition = "none";
    character.classList.add("clippy-dragging");
    character.classList.remove("clippy-state-walking", "clippy-state-sleeping", "clippy-state-playing", "clippy-state-happy");
    hideStatus();
    try { character.setPointerCapture(e.pointerId); } catch (err) {}
  });

  character.addEventListener("pointermove", function (e) {
    if (!isDragging) return;
    var dx = e.clientX - startPX, dy = e.clientY - startPY;
    if (Math.abs(dx) > 4 || Math.abs(dy) > 4) dragMoved = true;
    var rect = root.getBoundingClientRect();
    var newLeft = clamp(e.clientX - offsetX, 0, window.innerWidth - rect.width);
    var newTop = clamp(e.clientY - offsetY, 0, window.innerHeight - rect.height);
    root.style.left = newLeft + "px";
    root.style.top = newTop + "px";
  });

  function endDrag(e) {
    if (!isDragging) return;
    isDragging = false;
    character.classList.remove("clippy-dragging");
    lastInteraction = Date.now();
    root.style.transition = "";

    if (!dragMoved) {
      // treat as a click
      character.classList.remove("clippy-clicked");
      void character.offsetWidth;
      character.classList.add("clippy-clicked");
      showBubble(randomTip());
    } else {
      // landed after being dragged
      character.classList.add("clippy-state-happy");
      showStatus("\u2728", 1200);
      setTimeout(function () { character.classList.remove("clippy-state-happy"); }, 1400);
    }
  }

  character.addEventListener("pointerup", endDrag);
  character.addEventListener("pointercancel", endDrag);

  // ---- Autonomous activities ----
  function performWalk() {
    return new Promise(function (resolve) {
      var rect = root.getBoundingClientRect();
      var margin = 10;
      var maxLeft = window.innerWidth - rect.width - margin;
      var targetLeft = rand(margin, Math.max(margin, maxLeft));
      var distance = Math.abs(targetLeft - rect.left);
      var direction = targetLeft < rect.left ? -1 : 1;
      flip.style.transform = direction < 0 ? "scaleX(-1)" : "scaleX(1)";
      character.classList.add("clippy-state-walking");
      var duration = clamp(distance * 6, 900, 3500);
      root.style.transition = "left " + (duration / 1000) + "s ease-in-out";
      root.style.left = targetLeft + "px";
      setTimeout(function () {
        character.classList.remove("clippy-state-walking");
        resolve();
      }, duration);
    });
  }

  function performSleep() {
    return new Promise(function (resolve) {
      character.classList.add("clippy-state-sleeping");
      showStatus("\uD83D\uDCA4");
      var duration = rand(4000, 7000);
      setTimeout(function () {
        character.classList.remove("clippy-state-sleeping");
        hideStatus();
        resolve();
      }, duration);
    });
  }

  function performPlay() {
    return new Promise(function (resolve) {
      character.classList.add("clippy-state-playing");
      showStatus("\uD83C\uDF89", 1600);
      setTimeout(function () {
        character.classList.remove("clippy-state-playing");
        resolve();
      }, 1600);
    });
  }

  function performHappy() {
    return new Promise(function (resolve) {
      character.classList.add("clippy-state-happy");
      showStatus("\u2764\uFE0F", 1400);
      setTimeout(function () {
        character.classList.remove("clippy-state-happy");
        resolve();
      }, 1400);
    });
  }

  function performRandomActivity() {
    var choices = ["walk", "walk", "play", "sleep", "happy"];
    var choice = choices[randInt(0, choices.length - 1)];
    if (choice === "walk") return performWalk();
    if (choice === "play") return performPlay();
    if (choice === "sleep") return performSleep();
    return performHappy();
  }

  function activityLoop() {
    return wait(rand(6000, 13000)).then(function () {
      if (!document.getElementById("clippy-buddy-root")) return;
      if (isDragging || Date.now() - lastInteraction < 2500) {
        return activityLoop();
      }
      return performRandomActivity().then(activityLoop);
    });
  }
  activityLoop();
})();
