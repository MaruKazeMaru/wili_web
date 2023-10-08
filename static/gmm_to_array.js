function gmmToArray(gmmCnt, weights, avrs, vars, leftUp, rightDown, xStep, yStep){
    // determinet of covariance matrix
    var detVars = [];
    for(var i = 0; i < gmmCnt; ++i){
        detVars.push(vars[i][0] * vars[i][2] - vars[i][1] ** 2);
    }

    // inversed covariance matrix
    // upper triangular elemnts as 1-dim array
    var invVars = [];
    for (var i = 0; i < gmmCnt; ++i){
        var invVar = [];
        invVar.push(vars[i][2] / detVars[i]);
        invVar.push(-vars[i][1] / detVars[i]);
        invVar.push(vars[i][0] / detVars[i]);
        invVars.push(invVar);
    }
    // console.log(invVars);

    // weight * normalization constant
    var coefs = [];
    for(var i = 0; i < gmmCnt; ++i){
        var c = weights[i];
        c /= 6.283 // 2 * pi
        c /= Math.sqrt(detVars[i]);
        coefs.push(c);
    }
    // console.log(coefs);

    delete detVars;

    // values to make heatmap
    // this is a return value
    var vals = [];

    var x = leftUp[0];
    var y = leftUp[1];
    var dx = (rightDown[0] - leftUp[0]) / (xStep - 1);
    var dy = (rightDown[1] - leftUp[1]) / (yStep - 1);

    for(var k = 0; k < yStep; ++k){
        for(var j = 0; j < xStep; ++j){
            var val = 0.0;
            for(var i = 0; i < gmmCnt; ++i){
                var x_ = x - avrs[i][0];
                var y_ = y - avrs[i][1];
                var temp = invVars[i][0] * x_ * x_;
                temp += 2.0 *  invVars[i][1] * x_ * y_;
                temp += invVars[i][2] * y_ * y_;
                // console.log(temp);
                val += coefs[i] * Math.exp(-0.5 * temp);
            }

            vals.push(val);

            x += dx;
        }
        x = leftUp[0];
        y += dy;
    }

    return vals;
}