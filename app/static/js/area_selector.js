class RectangleMover {
    constructor(rectangle, callback, svg_obj, target_class) {
        this.rectangle = rectangle;
        this.isDragged = false;
        this.x_off = 0;
        this.y_off = 0;
        this.svg_obj = svg_obj;
        this.target_class = target_class;

        this.callback = (e) => {
          this.onMouseup(e, callback);
        }

        this.onMousedown = this.onMousedown.bind(this);
        this.onMouseup = this.onMouseup.bind(this);
        this.moverect = this.moverect.bind(this);
        this.rectangle.addEventListener('mousedown', this.onMousedown);

    }

    moverect(e) {
        let rectangle_box = this.rectangle.getBoundingClientRect();
        let svg_box = this.svg_obj.getBoundingClientRect();
        let sx = svg_box.x;
        let sy = svg_box.y;
        if (!this.isDragged) {
            this.x_off = e.clientX - rectangle_box.x;
            this.y_off = e.clientY - rectangle_box.y;
            this.isDragged = true;
        }

        const mouseX = e.clientX;
        const mouseY = e.clientY;

        let new_x = Math.min(svg_box.width - rectangle_box.width, Math.max(mouseX - this.x_off - sx, 0));
        let new_y = Math.min(svg_box.height - rectangle_box.height, Math.max(mouseY - this.y_off - sy, 0));

        this.rectangle.setAttribute('x', new_x);
        this.rectangle.setAttribute('y', new_y);
    }

    onMousedown(e) {
      if(e.button === 0){
          document.addEventListener('mousemove', this.moverect);
          document.addEventListener('mouseup', this.callback);
      }
    }

    onMouseup(e, callback) {
      if(e.button === 0){
        this.isDragged = false;
        document.removeEventListener('mousemove', this.moverect);
        document.removeEventListener('mouseup', this.callback);
        callback(e);
      }
    }
  
    get currentPosition(){
      const box = this.rectangle.getBoundingClientRect();
      return [box.x, box.y];
    }
    set currentPosition(value=null){
      const box = this.rectangle.getBoundingClientRect();
      this.cpf = [box.x, box.y];
    }
}


class Selector {
  constructor(container, xs, ys, strokeColor="", fillColor="black", fillOpacity="50%", class_="square", callback=null, recSize=25){
    this.container = container;
    this.xs = xs;
    this.ys = ys;
    this.recSize = recSize;
    this.class_ = class_;
    this.strokeColor = strokeColor;
    this.fillColor = fillColor;
    this.fillOpacity = fillOpacity;
    this.target = null;
    this.recMovers = [];
    this.callback = callback == null ? () => {} : callback;
    this.creationHandler = this.creationHandler.bind(this);
    this.removeListener = this.removeListener.bind(this);
    this.clear= this.clear.bind(this);
    this.creationisOn = false;
    
    let [path, rects] = this.buildElement();
    this.rects = rects;
    this.buildAnchors(rects);
    this.path = path;
  }

  buildAnchors(rects){
    for(let i=0; i<rects.length; i++){
      const cmd = i != 0 ? 'L' : 'M';
      const recMover = new RectangleMover(rects[i], this.callback, this.target, this.class);
      this.recMovers.push(recMover);
      this.createMovementMutationObserver(cmd, i*2, rects[i]);
      this.removeListener(rects[i]);
    }
  }

  get cxs(){
    return this.xs.map((x) => x+this.recSize/2);
  }

  get cys(){
    return this.ys.map((y) => y+this.recSize/2);
  }


  creationListener(){
    this.container.addEventListener('mousedown', this.creationHandler)
    this.creationisOn = true;
  }

  creationHandler(e){
    if(e.button === 1){
      const lside = this.container.getBoundingClientRect();
      const x = e.clientX - lside.x;
      const y = e.clientY - lside.y;
      this.appendRec(x, y);
      this.callback();
    };
  }

  handleMovementMutation(mutation, command, index) {
    if (mutation.type === 'attributes') {
      const path = document.querySelector('.selector-path');
      let d = path.getAttribute('d').split(' ');
      const width = mutation.target.getBBox().width;
      const height = mutation.target.getBBox().height;
  
      if(d[index] == undefined){
        d[index] = 'L'+mutation.target.getAttribute('x');
      }
      if(d[index+1] == undefined){
        d[index+1] = mutation.target.getAttribute('y');
      }
  
      if (mutation.attributeName === 'x') {
        const x = Number(mutation.target.getAttribute('x')) + width / 2;
        d[index] = command + String(x.toFixed(5));
      } else if (mutation.attributeName === 'y') {
        const y = Number(mutation.target.getAttribute('y')) + height / 2;
        d[index + 1] = String(y.toFixed(5));
      }
  
      path.setAttribute('d', d.join(' '));
    }
  }

  createMovementMutationObserver(command, index, targetRect) {
    const movement_observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        this.handleMovementMutation(mutation, command, index);
      });
    });
  
    movement_observer.observe(targetRect, { attributes: true });
  }


  buildElement(){
    const svgNS = "http://www.w3.org/2000/svg";
    this.target = document.createElementNS(svgNS, "svg");
    this.target.setAttribute("class", this.class_);

    const parentWidth = this.container.clientWidth;
    if (parentWidth) {
      const parentHeight = this.container.clientHeight;
      this.target.setAttribute("viewBox", `0 0 ${parentWidth} ${parentHeight}`);
    } else {
      this.target.setAttribute("viewBox", "0 0 1000 1000");
    }

    const path = this.addPath(this.strokeColor, this.fillColor, this.fillOpacity, this.cxs, this.cys);

    let rects = [];
    for (let i = 0; i < this.xs.length; i++) {
      rects.push(this.addRec(this.xs[i], this.ys[i]));
    }

    this.container.appendChild(this.target);
    return [path, rects];
  }

  addPath(strokeColor, fillColor, fillOpacity, xs, ys) {
    const svgNS = "http://www.w3.org/2000/svg";
    const path = document.createElementNS(svgNS, "path");
    path.setAttribute("d", xsys2pathd(xs, ys));
    path.setAttribute("class", "selector-path");
    path.setAttribute("stroke", strokeColor);
    path.setAttribute("fill", fillColor);
    path.setAttribute("fill-opacity", fillOpacity);
    return this.target.appendChild(path);
  }

  refreshPath(){
    this.rects = Array.from(this.target.querySelectorAll('rect'));
    let xs = [];
    let ys = [];
    for(let rc of this.rects){
      xs.push(Number(rc.getAttribute('x')));
      ys.push(Number(rc.getAttribute('y')));
    }
    this.xs = xs;
    this.ys = ys;
    this.path.setAttribute('d', xsys2pathd(this.cxs, this.cys));
  }

  resetPath(){
    this.rects = Array.from(this.target.querySelectorAll('rect'));
    let xs = [];
    let ys = [];
    let new_rects = []
    for(let rc of this.rects){
      let x = Number(rc.getAttribute('x'))
      let y = Number(rc.getAttribute('y'))
      let new_rect = rc.cloneNode(true)
      rc.parentNode.replaceChild(new_rect, rc);
      new_rects.push(new_rect);
      xs.push(x);
      ys.push(y);
    }
    console.log();
    this.xs = xs;
    this.ys = ys;
    this.buildAnchors(new_rects);
    this.path.setAttribute('d', xsys2pathd(this.cxs, this.cys));
  }
  
  clear(){
    console.log(this.rects);
    for(let rec of this.rects){
      rec.remove();
    }
    this.refreshPath();
    this.callback();
  }

  addRec(x, y) {
    const pos = this.rects === undefined ? this.xs.length : this.rects.length;
    const svgNS = "http://www.w3.org/2000/svg";
    const rect = document.createElementNS(svgNS, "rect");
    rect.setAttribute("class", "rec recn--"+String(pos));
    rect.setAttribute("x", x);
    rect.setAttribute("y", y);
    let createdObj = this.target.appendChild(rect);
    return createdObj;

  }

  removeListener(rec){
    rec.addEventListener('dblclick', (e) => {
        this.removeRec(e.target);
        this.callback();
    });
  }

  appendRec(x, y)
  {
    const pos = this.rects === undefined ? this.xs.length : this.rects.length;
    const cmd = pos !== 0 ? 'L' : 'M'
    const rec = this.addRec(x, y);
    this.xs.push(x);
    this.ys.push(y);
    this.rects.push(rec);
    const recMover = new RectangleMover(rec, this.callback, this.target, this.class);
    this.recMovers.push(recMover);
    this.removeListener(rec);
    this.createMovementMutationObserver(cmd, pos*2, rec);
    this.refreshPath();
  }

  removeRec(el){
    el.remove();
    this.resetPath();
  }

}


function xsys2pathd(xs, ys) {
  let pathd = '';
  for (let i = 0; i < xs.length; i++) {
    let x = Number(xs[i]).toFixed(5);
    let y = Number(ys[i]).toFixed(5);
    let cmd = i !== 0 ? ' L' : 'M';
    pathd += `${cmd}${x} ${y}`;
  }
  return pathd;
}

function sortCoordinates(xs, ys) {

  function calculateDistance(x, y) {
    return Math.sqrt(x * x + y * y);
  }

  const distances = xs.map((x, index) => ({
    index,
    distance: calculateDistance(x, ys[index]),
  }));

  distances.sort((a, b) => a.distance - b.distance);

  const sortedXs = distances.map((item) => xs[item.index]);
  const sortedYs = distances.map((item) => ys[item.index]);

  return [sortedXs,sortedYs];
}


export function create_selector(container, xs, ys, lsize, callback){
  const strokeColor = "";
  const fillColor = "black";
  const fillOpacity = "50%";
  let selector = new Selector(container, xs, ys, strokeColor, fillColor, fillOpacity, '.square', callback);
  selector.creationListener();
  return selector
}

// const strokeColor = "";
// const fillColor = "black";
// const fillOpacity = "50%";

// let container = document.querySelector('#svgc');
// const xs = [250, 750, 750, 250].map((a) => a/4);
// const ys = [250, 250, 750, 750].map((a) => a/4);
// let seletor = new Selector(container, xs, ys, strokeColor, fillColor, fillOpacity, '.square', () => {})g