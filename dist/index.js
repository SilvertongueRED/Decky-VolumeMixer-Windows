const manifest = {"name":"Mixer"};
const API_VERSION = 2;
const internalAPIConnection = window.__DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit;
if (!internalAPIConnection) {
    throw new Error('[@decky/api]: Failed to connect to the loader as as the loader API was not initialized. This is likely a bug in Decky Loader.');
}
let api;
try {
    api = internalAPIConnection.connect(API_VERSION, manifest.name);
}
catch {
    api = internalAPIConnection.connect(1, manifest.name);
    console.warn(`[@decky/api] Requested API version ${API_VERSION} but the running loader only supports version 1. Some features may not work.`);
}
if (api._version != API_VERSION) {
    console.warn(`[@decky/api] Requested API version ${API_VERSION} but the running loader only supports version ${api._version}. Some features may not work.`);
}
const callable = api.callable;
const toaster = api.toaster;
const definePlugin = (fn) => {
    return (...args) => {
        return fn(...args);
    };
};

var DefaultContext = {
  color: undefined,
  size: undefined,
  className: undefined,
  style: undefined,
  attr: undefined
};
var IconContext = SP_REACT.createContext && /*#__PURE__*/SP_REACT.createContext(DefaultContext);

var _excluded = ["attr", "size", "title"];
function _objectWithoutProperties(e, t) { if (null == e) return {}; var o, r, i = _objectWithoutPropertiesLoose(e, t); if (Object.getOwnPropertySymbols) { var n = Object.getOwnPropertySymbols(e); for (r = 0; r < n.length; r++) o = n[r], -1 === t.indexOf(o) && {}.propertyIsEnumerable.call(e, o) && (i[o] = e[o]); } return i; }
function _objectWithoutPropertiesLoose(r, e) { if (null == r) return {}; var t = {}; for (var n in r) if ({}.hasOwnProperty.call(r, n)) { if (-1 !== e.indexOf(n)) continue; t[n] = r[n]; } return t; }
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), true).forEach(function (r) { _defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function _defineProperty(e, r, t) { return (r = _toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == typeof i ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != typeof t || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r); if ("object" != typeof i) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function Tree2Element(tree) {
  return tree && tree.map((node, i) => /*#__PURE__*/SP_REACT.createElement(node.tag, _objectSpread({
    key: i
  }, node.attr), Tree2Element(node.child)));
}
function GenIcon(data) {
  return props => /*#__PURE__*/SP_REACT.createElement(IconBase, _extends({
    attr: _objectSpread({}, data.attr)
  }, props), Tree2Element(data.child));
}
function IconBase(props) {
  var elem = conf => {
    var {
        attr,
        size,
        title
      } = props,
      svgProps = _objectWithoutProperties(props, _excluded);
    var computedSize = size || conf.size || "1em";
    var className;
    if (conf.className) className = conf.className;
    if (props.className) className = (className ? className + " " : "") + props.className;
    return /*#__PURE__*/SP_REACT.createElement("svg", _extends({
      stroke: "currentColor",
      fill: "currentColor",
      strokeWidth: "0"
    }, conf.attr, attr, svgProps, {
      className: className,
      style: _objectSpread(_objectSpread({
        color: props.color || conf.color
      }, conf.style), props.style),
      height: computedSize,
      width: computedSize,
      xmlns: "http://www.w3.org/2000/svg"
    }), title && /*#__PURE__*/SP_REACT.createElement("title", null, title), props.children);
  };
  return IconContext !== undefined ? /*#__PURE__*/SP_REACT.createElement(IconContext.Consumer, null, conf => elem(conf)) : elem(DefaultContext);
}

// THIS FILE IS AUTO GENERATED
function FaSlidersH (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M496 384H160v-16c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h80v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h336c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zm0-160h-80v-16c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h336v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h80c8.8 0 16-7.2 16-16v-32c0-8.8-7.2-16-16-16zm0-160H288V48c0-8.8-7.2-16-16-16h-32c-8.8 0-16 7.2-16 16v16H16C7.2 64 0 71.2 0 80v32c0 8.8 7.2 16 16 16h208v16c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16v-16h208c8.8 0 16-7.2 16-16V80c0-8.8-7.2-16-16-16z"},"child":[]}]})(props);
}function FaPlus (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M416 208H272V64c0-17.67-14.33-32-32-32h-32c-17.67 0-32 14.33-32 32v144H32c-17.67 0-32 14.33-32 32v32c0 17.67 14.33 32 32 32h144v144c0 17.67 14.33 32 32 32h32c17.67 0 32-14.33 32-32V304h144c17.67 0 32-14.33 32-32v-32c0-17.67-14.33-32-32-32z"},"child":[]}]})(props);
}function FaMinus (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M416 208H32c-17.67 0-32 14.33-32 32v32c0 17.67 14.33 32 32 32h384c17.67 0 32-14.33 32-32v-32c0-17.67-14.33-32-32-32z"},"child":[]}]})(props);
}

// THIS FILE IS AUTO GENERATED
function BsGearFill (props) {
  return GenIcon({"attr":{"fill":"currentColor","viewBox":"0 0 16 16"},"child":[{"tag":"path","attr":{"d":"M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z"},"child":[]}]})(props);
}

const SettingsModalInputRow = (props) => {
    const ref = SP_REACT.useRef(null);
    return (SP_JSX.jsxs(DFL.Focusable, { style: { display: "flex", paddingTop: "8px" }, children: [SP_JSX.jsx("div", { style: { width: "100%" }, children: SP_JSX.jsx(DFL.TextField
                // @ts-ignore
                , { 
                    // @ts-ignore
                    ref: ref, value: props.value, onChange: (e) => props.onValueChanged(e.target.value) }) }), SP_JSX.jsx(DFL.DialogButton, { disabled: props.value === "" && props.isForNewFilter, style: {
                    width: '40px',
                    minWidth: 0,
                    padding: '10px 12px',
                    borderRadius: 0,
                }, onClick: () => {
                    props.onClick();
                    // @ts-ignore
                    if (props.isForNewFilter && ref.current)
                        ref.current.Focus();
                }, children: props.isForNewFilter ? SP_JSX.jsx(FaPlus, { style: { display: 'block' } }) : SP_JSX.jsx(FaMinus, { style: { display: 'block' } }) })] }));
};
const SettingsModal = (props) => {
    const nextFilterId = SP_REACT.useRef(0);
    const [filters, setFilters] = SP_REACT.useState([]);
    const [newFilterValue, setNewFilterValue] = SP_REACT.useState("");
    const newFilterOnClick = () => {
        setFilters(prev => [...prev, { key: nextFilterId.current++, value: newFilterValue }]);
        setNewFilterValue("");
    };
    const onFilterChanged = (key, value) => {
        setFilters(prev => prev.map(v => v.key === key ? { ...v, value } : v));
    };
    const deleteFilterOnClick = (key) => {
        setFilters(prev => prev.filter((v) => v.key !== key));
    };
    const [boostLimit, setBoostLimit] = SP_REACT.useState(0);
    const saveBtnOnClick = async () => {
        const res = await props.onSave({
            filters: filters.filter((v) => v.value !== "").map(v => v.value),
            boostLimit: boostLimit,
        });
        toaster.toast({
            title: "Volume Mixer",
            body: res ? "Settings saved successfully" : "Failed to save settings, check values and try again",
            critical: !res,
        });
    };
    SP_REACT.useEffect(() => {
        let alive = true;
        const load = async () => {
            try {
                const data = await props.getSettings();
                if (alive) {
                    setFilters(data.filters.map(filter => ({ key: nextFilterId.current++, value: filter })));
                    setBoostLimit(data.boostLimit);
                }
            }
            catch (e) {
                toaster.toast({ title: "Volume Mixer", body: "Failed to get settings", critical: true });
                console.error(e);
            }
        };
        load();
        return () => { alive = false; };
    }, []);
    return (SP_JSX.jsxs(DFL.ConfirmModal, { ...props, strTitle: "Mixer settings", strOKButtonText: "Save", strCancelButtonText: "Cancel", onOK: saveBtnOnClick, children: [SP_JSX.jsxs(DFL.Focusable, { children: [SP_JSX.jsx("span", { className: DFL.staticClasses.PanelSectionTitle, children: "Playback filters" }), SP_JSX.jsx("span", { children: "Regular expressions in Python format to exclude playbacks from the list" }), SP_JSX.jsx(SettingsModalInputRow, { isForNewFilter: true, value: newFilterValue, onValueChanged: setNewFilterValue, onClick: newFilterOnClick }, "new-filter"), filters.map((filter) => SP_JSX.jsx(SettingsModalInputRow, { isForNewFilter: false, value: filter.value, onValueChanged: (v) => onFilterChanged(filter.key, v), onClick: () => deleteFilterOnClick(filter.key) }, filter.key))] }), SP_JSX.jsx(DFL.Focusable, { style: { marginTop: "20px" }, children: SP_JSX.jsx(DFL.SliderField, { bottomSeparator: "none", showValue: true, editableValue: true, label: "Boost limit", description: "Set to 0 to disable boost", min: 0, max: 100, step: 5, value: boostLimit, onChange: setBoostLimit }) })] }));
};

const getPlaybacks = callable("get_playbacks");
const setVolume = callable("set_volume");
const resetVolumes = callable("reset_volumes");
const getSettings = callable("get_settings");
const saveSettings = callable("save_settings");
const setExcluded = callable("set_excluded");
function Content() {
    const [settings, setSettings] = SP_REACT.useState();
    const [playbacks, setPlaybacks] = SP_REACT.useState([]);
    const [manage, setManage] = SP_REACT.useState(false);
    const lastChanged = SP_REACT.useRef(0);
    SP_REACT.useEffect(() => {
        let alive = true;
        const load = async () => {
            try {
                const data = await getSettings();
                if (alive)
                    setSettings(data);
            }
            catch (e) {
                toaster.toast({ title: "Volume Mixer", body: "Failed to get settings", critical: true });
                console.error(e);
            }
        };
        load();
        return () => { alive = false; };
    }, []);
    SP_REACT.useEffect(() => {
        let alive = true;
        const load = async () => {
            if (!alive)
                return;
            if (Date.now() - lastChanged.current < 2000) {
                setTimeout(load, 1000);
                return;
            }
            try {
                const data = await getPlaybacks();
                if (alive) {
                    setPlaybacks(data);
                    setTimeout(load, 1000);
                }
            }
            catch (e) {
                toaster.toast({ title: "Volume Mixer", body: "Failed to load playbacks", critical: true });
                console.error(e);
            }
        };
        load();
        return () => { alive = false; };
    }, []);
    const onVolumeChange = async (id, volume) => {
        lastChanged.current = Date.now();
        setPlaybacks(prev => prev.map(p => p.id === id ? { ...p, volume } : p));
        if (!(await setVolume(id, volume))) {
            toaster.toast({ title: "Volume Mixer", body: "Failed to set volume", critical: true });
        }
    };
    const onResetClicked = async () => {
        lastChanged.current = Date.now();
        setPlaybacks(prev => prev.map(p => ({ ...p, volume: 100 })));
        await resetVolumes().catch(() => toaster.toast({ title: "Volume Mixer", body: "Failed to reset volumes", critical: true }));
    };
    const onToggleExcluded = async (name, excluded) => {
        lastChanged.current = Date.now();
        setPlaybacks(prev => prev.map(p => p.name === name ? { ...p, excluded } : p));
        if (!(await setExcluded(name, excluded))) {
            toaster.toast({ title: "Volume Mixer", body: "Failed to update app", critical: true });
        }
    };
    const visible = playbacks.filter(p => !p.excluded);
    const centerNote = (text, key) => SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { className: DFL.staticClasses.PanelSectionTitle, style: { textAlign: "center", display: "block", marginTop: "11px" }, children: text }) }, key);
    if (manage) {
        const seenNames = new Set();
        const uniqueByName = playbacks.filter(p => { if (seenNames.has(p.name)) return false; seenNames.add(p.name); return true; });
        return (SP_JSX.jsxs(DFL.PanelSection, { children: [
            SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("span", { children: "Turn an app off to hide it from the mixer." }) }, "manage-header"),
            ...uniqueByName.map((p) => SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ToggleField, { label: p.name, checked: !p.excluded, onChange: (value) => onToggleExcluded(p.name, !value) }) }, "t-" + p.name)),
            uniqueByName.length === 0 ? centerNote("Nothing is playing", "empty") : null,
            SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { bottomSeparator: "none", layout: "below", onClick: () => setManage(false), children: "Done" }) }, "done")
        ] }));
    }
    return (SP_JSX.jsxs(DFL.PanelSection, { children: [
        ...visible.map((playback, i, all) => (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.SliderField, { bottomSeparator: i === all.length - 1 ? "standard" : "none", showValue: true, editableValue: true, label: playback.name, description: playback.mediaName?.slice(0, 44), min: 0, max: 100 + (settings?.boostLimit ?? 0), step: 1, value: playback.volume, onChange: (volume) => onVolumeChange(playback.id, volume) }) }, playback.id))),
        playbacks.length === 0 ? centerNote("Nothing is playing", "empty") : null,
        (playbacks.length > 0 && visible.length === 0) ? centerNote("All apps hidden", "allhidden") : null,
        (visible.length > 0) ? SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { bottomSeparator: "none", layout: "below", onClick: onResetClicked, children: "Reset" }) }, "reset") : null,
        (playbacks.length > 0) ? SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { bottomSeparator: "none", layout: "below", onClick: () => setManage(true), children: "Hide apps" }) }, "hideapps") : null
    ] }));
}
function TitleView() {
    return (SP_JSX.jsxs(DFL.Focusable, { style: { display: "flex", padding: 0, width: "100%", justifyContent: "space-between" }, children: [SP_JSX.jsx("div", { className: DFL.staticClasses.Title, style: { padding: 0 }, children: "Volume Mixer" }), SP_JSX.jsx(DFL.DialogButton, { style: { height: '28px', width: '40px', minWidth: 0, padding: '10px 12px' }, onClick: () => DFL.showModal(SP_JSX.jsx(SettingsModal, { getSettings: getSettings, onSave: saveSettings })), children: SP_JSX.jsx(BsGearFill, { style: { marginTop: '-4px', display: 'block' } }) })] }));
}
var index = definePlugin(() => {
    return {
        name: "Volume Mixer",
        titleView: SP_JSX.jsx(TitleView, {}),
        content: SP_JSX.jsx(Content, {}),
        icon: SP_JSX.jsx(FaSlidersH, {}),
    };
});
export { index as default };
