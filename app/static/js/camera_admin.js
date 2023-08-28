import { create_selector } from "./area_selector.js";

function scaleWebView(xs, ys, videoShape, webviewShape, squareSize) {
    const scaleX = webviewShape[0] / videoShape[0];
    const scaleY = webviewShape[1] / videoShape[1];
  
    const scaledXs = xs.map((x) => x * scaleX - squareSize / 2);
    const scaledYs = ys.map((y) => y * scaleY - squareSize / 2);
  
    return [scaledXs, scaledYs];
  }
  
  function unscaleWebView(scaledXs, scaledYs, videoShape, webviewShape, squareSize) {
      const scaleX = videoShape[0] / webviewShape[0];
      const scaleY = videoShape[1] / webviewShape[1];
    
      const unscaledXs = scaledXs.map((x) => x * scaleX + squareSize/2);
      const unscaledYs = scaledYs.map((y) => y*scaleY + squareSize/2);
    
      return [unscaledXs, unscaledYs];
  }
  
  async function update_seg(xsys) {
    try {
      xsys = xsys[0].map((x, i) => [x, xsys[1][i]]);
      const postData = {
        xsys: xsys,
      };
  
      const url = '/inference/set_seg';
  
      const options = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      };
  
      const response = await fetch(url, options);
  
      if (!response.ok) {
          console.log(response.error);
      }
  
      const data = await response.json();
  
  
      return data;
    } catch (error) {
      console.error('Error:', error);
      throw error;
    }
  }
    
  
  class CoordinateManager{
      constructor(xs, ys, side, svg, videoShape, webviewShape, squareSize){
          this.xs = xs;
          this.ys = ys;
          this.videoShape = videoShape;
          this.webviewShape = webviewShape;
          this.squareSize = squareSize;
          this.svg = svg;
          this.updateCoordinateEvent = this.updateCoordinateEvent.bind(this);
      }
      
      updateCoordinateEvent(e){
          let recs = this.svg.querySelectorAll('.rec');
          let nxs = [];
          let nys = [];
          for(let r of recs){
              nxs.push(r.getAttribute('x'));
              nys.push(r.getAttribute('y'));
          }
          if(String(nxs) !== String(this.xs)){
              this.xs = nxs;
          }
          if(String(nys) !== String(this.ys)){
              this.ys = nys;
          }
          let xsys = unscaleWebView(this.xs, this.ys, this.videoShape, this.webviewShape, this.squareSize);
          update_seg(xsys);
      }
      
  }
  
  async function setupContainer(){
      let r = await fetch('/inference/get_seg?format=xsys').then((r) => r.json());
      let xsys = r.xsys;
      let videoShape = r.shape;
      let container = document.querySelector('#svgc');
      let cStyle = window.getComputedStyle(container)
      let size = [Number(cStyle.width.replace('px', '')), Number(cStyle.height.replace('px', ''))];
      container.style.background = "url('/inference/footage_stream/')";
      container.style.backgroundSize = `${size[0]}px ${size[1]}px`;
  
      const [xs, ys] = scaleWebView(xsys[0], xsys[1], videoShape, size, 20);
  
      let cManager = new CoordinateManager(xs,ys, 20, container, videoShape, size, 20);
      let selector = create_selector(container, xs, ys, 20, cManager.updateCoordinateEvent);
      document.getElementById("cleanButton").onclick = selector.clear;
  }
  
  setupContainer();