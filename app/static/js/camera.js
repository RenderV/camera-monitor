let container = document.querySelector('#svgc');
let cStyle = window.getComputedStyle(container);
let size = [cStyle.width, cStyle.height];
container.style.background = "url('/inference/footage_stream/')";
container.style.backgroundSize = `${size[0]} ${size[1]}`;