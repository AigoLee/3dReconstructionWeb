if (!String.prototype.endsWith) {
	String.prototype.endsWith = function(searchString, position) {
		var subjectString = this.toString();
		if (typeof position !== 'number' || !isFinite(position) || Math.floor(position) !== position || position > subjectString.length) {
			position = subjectString.length;
		}
		position -= searchString.length;
		var lastIndex = subjectString.indexOf(searchString, position);
		return lastIndex !== -1 && lastIndex === position;
	};
}

function viewer(container, options) {
	var roll = options.roll || 0.0;
	var pitch = options.pitch || 0.0;
	var yaw = options.yaw || 0.0;
	var pointSize = options.pointSize || 0.2; //0.015 0.1
	var homeIP = options.homeIP || '127.0.0.1:5000';

	document.getElementById("homeip").href = 'http://'+ homeIP;

	function buildColor(v) {
		var pi = 3.151592;
		var r = Math.cos(v*2*pi + 0) * 0.5 + 0.5;
		var g = Math.cos(v*2*pi + 2) * 0.5 + 0.5;
		var b = Math.cos(v*2*pi + 4) * 0.5 + 0.5;

		return new THREE.Color(r, g, b);
	}

	var scene = null;
	var renderer = null;
	var camera = null;

	// Draw the progressbar on the middle
	var left = Math.round( (window.innerWidth - 400)/2 );
	$("#progressbar-container").css("left",left + "px");

	// Scene
	scene = new THREE.Scene();
	scene.fog = new THREE.FogExp2(0x000000, 0.0009);

	// Camera
	var camera = new THREE.PerspectiveCamera(10, window.innerWidth / window.innerHeight, 0.1, 1000);
	camera.position.z = 100;
	//camera.up = new THREE.Vector3(0,0,1);

	if (!Detector.webgl) {
		$("#progressbar-container").hide();
		Detector.addGetWebGLMessage();
		return;
	}

	renderer = new THREE.WebGLRenderer();
	renderer.setSize(window.innerWidth-17, window.innerHeight-55);

	// 渲染场景
	function render() {
		renderer.render(scene, camera);
	}

	// 设置控件
	var controls = new THREE.OrbitControls( camera );
	controls.rotateSpeed = 1.0;
	controls.zoomSpeed = 2.2;
	controls.panSpeed = 0.8;
	controls.enableDamping = true;
	controls.dampingFactor = 0.3;
	controls.keys = [65, 17, 18];
	controls.addEventListener('change', render);

	var geometry = new THREE.SphereGeometry( 0.1, 32, 32 );
	var material = new THREE.MeshBasicMaterial({
		color: 0xffff00,
		transparent: true,
		opacity: 0.5
	});
	controls.visualizer = new THREE.Mesh( geometry, material );
	scene.add( controls.visualizer );
	controls.visualizer.visible = false;

	function animate() {
		requestAnimationFrame(animate);
		controls.update();
	}

	// 初始化几何
	var geometry = new THREE.Geometry();
	var material = new THREE.PointsMaterial({size:pointSize, vertexColors:true});
	var pointcloud = new THREE.Points(geometry, material);
	scene.add(pointcloud);

	// 添加canvas, render
	console.log(container);
	container.append(renderer.domElement);

	// 加载点云
	var colors = {
		x: {
			data: [],
			valid: 0
		},
		y: {
			data: [],
			valid: 0
		},
		z: {
			data: [],
			valid: 0
		},
		rgb: {
			data: [],
			valid: 0
		}
	};

	var cname = getUrlParameter('color');
	if(cname == undefined)
		cname = 'rgb';

	function recomputeColorChannel(name, stats, numPoints) {
		stats = stats[name];
		var data = colors[name].data;

		if(stats.min >= stats.max)
		{
			// 延伸到 vertices.length
			for(var i = data.length; i < geometry.vertices.length; ++i)
				data[i] = new THREE.Color(0.87, 0.87, 0.87);

			return;
		}

		var start = stats.dirty ? 0 : colors[name].valid;
		if(stats.dirty)
			console.log('color channel dirty');

		for (var i=start; i < numPoints; i++)
		{
			var z = geometry.vertices[i][name];
			t = (z-stats.min)/(stats.max-stats.min);
			if(isNaN(t))
			{
				data[i] = new THREE.Color(0);
				continue;
			}
			data[i] = buildColor(t);
		}

		// 延伸到 vertices.length
		for(var i = numPoints; i < geometry.vertices.length; ++i)
			data[i] = new THREE.Color(0.87, 0.87, 0.87);

		colors[name].valid = numPoints;
	};

	// 改变点云颜色
	function changeColor(color_mode)
	{
		console.log('Switching to color mode', color_mode);

		if(colors[color_mode].valid != geometry.vertices.length)
		{
			recomputeColorChannel(color_mode, finalStats, geometry.vertices.length);
		}

		pointcloud.geometry.colors = colors[color_mode].data;
		pointcloud.geometry.colorsNeedUpdate = true;
	}

	// 处理颜色和点云大小
	function onKeyDown(evt) {
		// 监听按键增加/减小点云大小
		if (evt.keyCode == 189 || evt.keyCode == 109 || evt.keyCode == 173)
		{	
			if(pointcloud.material.size - 0.03 > 0){
				pointcloud.material.size -= 0.03;	//0.003
				pointcloud.material.needsUpdate = true;
			}
			else{
				alert("点云尺寸太小！");
			}
		}
		if (evt.keyCode == 187 || evt.keyCode == 107 || evt.keyCode == 171)
		{
			pointcloud.material.size += 0.03;
			pointcloud.material.needsUpdate = true;
		}

		if (evt.keyCode == 49) changeColor('x');
		if (evt.keyCode == 50) changeColor('y');
		if (evt.keyCode == 51) changeColor('z');
		if (evt.keyCode == 52) changeColor('rgb');

		render();
	}

	var bufferSize = 0;
	var finalStats = null;

	var load = null;
	var filename = options.filename;

	load = loadPCDFile;
	
	var transform = new THREE.Matrix4();
	var euler = new THREE.Euler(roll, pitch, yaw, 'XYZ');
	transform.makeRotationFromEuler(euler);

	load(filename, transform, geometry.vertices, colors['rgb'].data,
		function(stats, numPoints) {
			colors['rgb'].valid = numPoints;
			finalStats = stats;

			if(cname != 'rgb')
				recomputeColorChannel(cname, stats, numPoints);

			console.log('progress', numPoints);

			if(geometry.vertices.length != bufferSize) {
				scene.remove(pointcloud);
				pointcloud.geometry.dispose();
				pointcloud.material.dispose();

				var vertices = geometry.vertices;

				geometry = new THREE.Geometry();
				geometry.dynamic = true;
				geometry.vertices = vertices;
				geometry.colors = colors[cname].data;

				pointcloud = new THREE.Points(geometry, material);
				scene.add(pointcloud);
			}
			else
			{
				geometry.verticesNeedUpdate = true;
				geometry.colorsNeedUpdate = true;
			}

			bufferSize = geometry.vertices.length;

			render();
		},
		function() {
			// 移除控件
			$("#progressbar-container").hide();
			$("#controls-browser").show();

			document.addEventListener("keydown", onKeyDown, false);
			document.getElementById("myBtn+").addEventListener("click", function()
			{	
				const ke = new KeyboardEvent('keydown', {
					bubbles: true, cancelable: true, keyCode: 107
				});
				document.body.dispatchEvent(ke);
				document.getElementById("demo").innerHTML = "点云尺寸: "+ pointcloud.material.size.toFixed(2);

			});
			document.getElementById("myBtn-").addEventListener("click", function()
			{
				const ke = new KeyboardEvent('keydown', {
					bubbles: true, cancelable: true, keyCode: 109
				});
				document.body.dispatchEvent(ke);
				document.getElementById("demo").innerHTML = "点云尺寸: "+ pointcloud.material.size.toFixed(2);

			});
		}
	);

	render();
	animate();
}
