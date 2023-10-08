function showHeatmap(canvasId, width, height, vals){
    // console.log(vals);
    var cnvs = document.getElementById(canvasId);
    var ctx = cnvs.getContext("2d");
    cnvs.width = width;
    cnvs.height = height;

    var val_max = vals[0];
    var l = width * height;
    for(var i = 1; i < l; ++i){
        if(val_max < vals[i]){
            val_max = vals[i];
        }
    }
    console.log(val_max);

    imgData = ctx.getImageData(0, 0, width, height);
    for(var j = 0; j < height; ++j){
        var d = j * width;
        for(var i = 0; i < width; ++i){
            var h = vals[d + i] / val_max;
            h = Math.floor(h * 255);
            // console.log(h);
            imgData.data[4 * (d + i) + 0] = h;
            imgData.data[4 * (d + i) + 1] = h;
            imgData.data[4 * (d + i) + 2] = h;
            imgData.data[4 * (d + i) + 3] = 255;
        }
    }
    ctx.putImageData(imgData, 0, 0);
}