var imageUpload = document.getElementById('image-upload');
var uploadedImage = document.getElementById('uploaded-image');
var annotationCanvas = document.getElementById('annotation-canvas');
var bboxLabelInput = document.getElementById('bbox-label');
var addBboxButton = document.getElementById('add-bbox');
var saveDataButton = document.getElementById('save-data');
var bboxCoordinates = document.getElementById('bbox-coordinates');

var bboxes = [];
var colors = ['red', 'blue', 'green', 'yellow'];
var colorIndex = 0;
var selectedBbox = null;
var dragStartX = 0;
var dragStartY = 0;
var resizeHandleRadius = 5;
var resizing = false;
var resizeHandle = null;


// 1. 박스 추가 //
addBboxButton.addEventListener('click', function() {
  var startX = parseInt(document.getElementById('startX').value);
  var startY = parseInt(document.getElementById('startY').value);

  var endX = parseInt(document.getElementById('endX').value);
  var endY = parseInt(document.getElementById('endY').value);

  var width = endX - startX
  var height = endY - startY
  var label = document.querySelector('input[name="bbox-label"]:checked').value;

  if (isNaN(startX) || isNaN(startY) || isNaN(endX) || isNaN(endY)) {
    alert('올바른 값을 입력하세요.');
    return;
  }

  var bbox = {
    label: label,
    startX: startX,
    startY: startY,
//    endX: endX,
//    endY: endY,
    width: width,
    height: height,
    color: colors[colorIndex]

  };

  bboxes.push(bbox);
  colorIndex = (colorIndex + 1) % colors.length;
  drawBoundingBox();
  updateCoordinates();
});




annotationCanvas.addEventListener('mousedown', function(e) {
  var mouseX = e.offsetX;
  var mouseY = e.offsetY;

  for (var i = bboxes.length - 1; i >= 0; i--) {
    var bbox = bboxes[i];
    if (isInsideResizeHandle(mouseX, mouseY, bbox)) {
      resizing = true;
      resizeHandle = getResizeHandle(mouseX, mouseY, bbox);
      return;
    } else if (mouseX >= bbox.startX && mouseX <= bbox.startX + bbox.width &&
        mouseY >= bbox.startY && mouseY <= bbox.startY + bbox.height) {
      selectedBbox = bbox;
      dragStartX = mouseX - bbox.startX;
      dragStartY = mouseY - bbox.startY;
      return;
    }
  }
});


annotationCanvas.addEventListener('mousemove', function(e) {
  var mouseX = e.offsetX;
  var mouseY = e.offsetY;

  if (resizing) {
    var newWidth = mouseX - selectedBbox.startX;
    var newHeight = mouseY - selectedBbox.startY;
    if (newWidth > 0 && newHeight > 0) {
      selectedBbox.width = newWidth;
      selectedBbox.height = newHeight;
      drawBoundingBox();
      updateCoordinates();
    }
  } else if (selectedBbox !== null) {
    selectedBbox.startX = mouseX - dragStartX;
    selectedBbox.startY = mouseY - dragStartY;
    drawBoundingBox();
    updateCoordinates();
  } else if (isInsideAnyResizeHandle(mouseX, mouseY)) {
    annotationCanvas.style.cursor = 'nwse-resize';
  } else {
    annotationCanvas.style.cursor = 'default';
  }
});

annotationCanvas.addEventListener('mouseup', function() {
  resizing = false;
  selectedBbox = null;
});

function drawBoundingBox() {
  var ctx = annotationCanvas.getContext('2d');
  ctx.clearRect(0, 0, annotationCanvas.width, annotationCanvas.height);
  ctx.lineWidth = 1;

  for (var i = 0; i < bboxes.length; i++) {
    var bbox = bboxes[i];
    ctx.strokeStyle = bbox.color;
    ctx.strokeRect(bbox.startX, bbox.startY, bbox.width, bbox.height);
    drawResizeHandles(ctx, bbox);
    ctx.fillStyle = bbox.color;
    ctx.fillRect(bbox.startX, bbox.startY - 20, bbox.label.length * 7, 20);
    ctx.fillStyle = 'white';
    ctx.font = '12px Arial';
    ctx.fillText(bbox.label, bbox.startX, bbox.startY - 5);
  }
}

function drawResizeHandles(ctx, bbox) {
  var handles = getResizeHandles(bbox);
  ctx.fillStyle = 'black';  // 색깔

  for (var i = 0; i < handles.length; i++) {
    var handle = handles[i];
    var handleSize = resizeHandleRadius / 2; // 크기를 작게 설정
    ctx.fillRect(handle.x - handleSize, handle.y - handleSize, handleSize * 2, handleSize * 2);
  }
}

function getResizeHandles(bbox) {
  var handles = [
    { x: bbox.startX, y: bbox.startY },
    { x: bbox.startX + bbox.width, y: bbox.startY },
    { x: bbox.startX + bbox.width, y: bbox.startY + bbox.height },
    { x: bbox.startX, y: bbox.startY + bbox.height }
  ];
  return handles;
}

function isInsideResizeHandle(x, y, bbox) {
  var handles = getResizeHandles(bbox);
  for (var i = 0; i < handles.length; i++) {
    var handle = handles[i];
    if (x >= handle.x - resizeHandleRadius && x <= handle.x + resizeHandleRadius &&
        y >= handle.y - resizeHandleRadius && y <= handle.y + resizeHandleRadius) {
      return true;
    }
  }
  return false;
}

function getResizeHandle(x, y, bbox) {
  var handles = getResizeHandles(bbox);
  for (var i = 0; i < handles.length; i++) {
    var handle = handles[i];
    if (x >= handle.x - resizeHandleRadius && x <= handle.x + resizeHandleRadius &&
        y >= handle.y - resizeHandleRadius && y <= handle.y + resizeHandleRadius) {
      return handle;
    }
  }
  return null;
}

function isInsideAnyResizeHandle(x, y) {
  for (var i = 0; i < bboxes.length; i++) {
    var bbox = bboxes[i];
    if (isInsideResizeHandle(x, y, bbox)) {
      return true;
    }
  }
  return false;
}

function updateCoordinates() {
  bboxCoordinates.innerHTML = '';
  for (var i = 0; i < bboxes.length; i++) {
    var bbox = bboxes[i];
    var bboxInfo = document.createElement('p');
    bboxInfo.innerText = `${bbox.label}: x: ${bbox.startX} ~ ${bbox.startX + bbox.width}, y: ${bbox.startY} ~ ${bbox.startY + bbox.height}`;
    bboxCoordinates.appendChild(bboxInfo);
  }
}