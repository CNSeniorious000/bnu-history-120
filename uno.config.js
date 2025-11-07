import presetUno from "@unocss/preset-uno"

export default {
    cli: {
        entry: {
            patterns: ["./templates/*.jinja2"],
            outFile: "./static/uno.css"
        }
    },
    presets: [presetUno({ dark: "media" })]
}