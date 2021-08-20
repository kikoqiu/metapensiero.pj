export function _assert(comp, msg) {
	msg = (msg || "Assertion failed.");
	if ((! comp)) {
		throw new Error(msg);
	}
}
export function _in(left, right) {
	if (((right instanceof Array) || ((typeof right) === "string"))) {
		return (right.indexOf(left) > (- 1));
	} else {
		return (left in right);
	}
}
export function in_es6(left, right) {
	if (((right instanceof Array) || ((typeof right) === "string"))) {
		return (right.indexOf(left) > (- 1));
	} else {
		if (((right instanceof Map) || (right instanceof Set) || (right instanceof WeakMap) || (right instanceof WeakSet))) {
			return right.has(left);
		} else {
			return (left in right);
		}
	}
}
export function set_class_decorators(cls, decos) {
	function reducer(val, deco) {
		return deco(val, cls);
	}
	return decos.reduce(reducer, cls);
}
export function set_decorators(cls, props) {
	var deco, decos;
	var _pj_a = props;
	for (let p in _pj_a) {
		if (_pj_a.hasOwnProperty(p)) {
			decos = props[p];
			function reducer(val, deco) {
				return deco(val, cls, p);
			}
			deco = decos.reduce(reducer, cls.prototype[p]);
			if ((((! ((deco instanceof Function) || (deco instanceof Map) || (deco instanceof WeakMap))) && (deco instanceof Object)) && (("value" in deco) || ("get" in deco)))) {
				delete cls.prototype[p];
				Object.defineProperty(cls.prototype, p, deco);
			} else {
				cls.prototype[p] = deco;
			}
		}
	}
}
export function set_properties(cls, props) {
	var desc, value;
	var _pj_a = props;
	for (let p in _pj_a) {
		if (_pj_a.hasOwnProperty(p)) {
			value = props[p];
			if (((((! ((value instanceof Map) || (value instanceof WeakMap))) && (value instanceof Object)) && ("get" in value)) && (value.get instanceof Function))) {
				desc = value;
			} else {
				desc = {"value": value, "enumerable": false, "configurable": true, "writable": true};
			}
			Object.defineProperty(cls.prototype, p, desc);
		}
	}
}


export function* mapg(it, mappers, filters){
	if(mappers.length==1){
		for(let a of it){
			if(filters[0]!=null && !filters[0](a)){
				continue;
			}
			yield mappers[0](a);
		}
		return;
	}

	if(mappers.length==2){
		for(let a of it){
			if(filters[0]!=null && !filters[0](a)){
				continue;
			}
			for(let b of mappers[0](a)){
				if(filters[1]!=null && !filters[1](a,b)){
					continue;
				}
				yield mappers[1](a,b);
			}
		}
		return;
	}


	if(mappers.length==3){
		for(let a of it){
			if(filters[0]!=null && !filters[0](a)){
				continue;
			}
			for(let b of mappers[0](a)){
				if(filters[1]!=null && !filters[1](a,b)){
					continue;
				}
				for(let c of mappers[1](a,b)){
					if(filters[2]!=null && !filters[2](a,b,c)){
						continue;
					}
					yield mappers[2](a,b,c);
				}
			}
		}
		return;
	}

	throw new Error('not implemented');
}
export function mapl(it, mappers, filters){
	return [...mapg(it,mappers,filters)];
}

export class slice {
	constructor(lower, upper, step) {
		this.lower = lower;
		this.upper = upper;
		this.step = step;
		return this;
	}
}
export function __getitem__(target,key){	
	/*if(Array.isArray(value)){
		return value[key];
	}
	if(Array.isArray(key) || key instanceof slice){		
	}*/
	if('__getitem__' in target){
		return target.__getitem__(key);
	}
	return target[key];
}
export function __setitem__(target,key,value){	
	/*if(Array.isArray(value)){
		return value[key];
	}
	if(Array.isArray(key) || key instanceof slice){		
	}*/
	if('__setitem__' in target){
		return target.__setitem__(key,value);
	}
	return target[key]=value;
}

export function pythonnew(cls,...args){
	return new cls(...args);
}

export function pythonset(cls,...args){
	return new Set();
}
export function ext_acc(...acc) {
	var kwargs, last;
	last = acc.slice((- 1))[0];
	kwargs = null;
	if ((last instanceof kw)) {
		kwargs = last.values;
		return [acc.slice(0, (- 1)), kwargs];
	}
	return [acc];
}


















export function *range(b,e,st=1){
    if(e===undefined){
        e=b;
        b=0;
    }
    for(let i=b;i<e;i+=st){
        yield i;
    }
}
export function round(a){
	return Math.round(a);
}
export class dict {
	constructor(values) {
		this.values = values;
	}
	setdefault(key, val) {
		if ((! (key in this))) {
			this[key] = val;
		}
	}
}

export class kw extends dict{
}

export function staticmethod(f){
	return f;
}
export function frozenset(...args){
	return pythonset(args);
}

var globals={range,round,dict,staticmethod,}
for(let a of Object.keys(globals)){
	globalThis[a]=globals[a];
}





    

