## 北师大 120 周年校史整理

本站资料由 2020 级北师珠本科生 **蔡伟俊**、**唐佳** 人工收集整理自海量文献，后由 **徐景喆**、[**庄毅辉**](https://github.com/CNSeniorious000 "Muspi Merol") 略加处理。项目成员还包括潘泽嘉师兄和姜赢导师。

> 本大创项目最初诞生于 [北师大120周年校庆](https://120th.bnu.edu.cn/) 前后，虽然这个项目组最终由于以我为首的一些拖延不欢而散，但毕竟这些资料基本完整，于是这个网站仍然被维护，作为当年成果的一个 snapshot，希望能给互联网带来一些价值。
>
> 如果在浏览本站的你有什么纠错/建议或者任何想说的，欢迎在 [Issues](https://github.com/CNSeniorious000/bnu-history-120/issues) 或者 [Discussions](https://github.com/CNSeniorious000/bnu-history-120/discussions) 版块留言！
>
> 由于这是我第一次接触 Web 时的作品，当时工程知识几乎为 0，所以技术栈比较传统，加上我个人的一些 hack，可能很多地方比较怪异，请见谅！这些技术债导致这个项目维护成本较高，因此可视作是一个 archived 的状态。

### Deployed | 开始浏览

你可以通过 [bnu.muspimerol.site](https://bnu.muspimerol.site/) 访问本网站。网站由 Jinja2 简单地渲染自一些 markdown 文件，现在通过一个 SSG 脚本静态化，部署到 [Vercel](https://bnu120.vercel.app/) 和 [Netlify](https://bnu120.netlify.app/) 上。你也可以在 [这个目录](https://github.com/CNSeniorious000/bnu-history-120/tree/master/data) 直接浏览所有 markdown 文档。我们也提供开放 API，文档见 [Swagger](https://bnu120.space/docs) / [ReDoc](https://bnu120.space/redoc)

### Development | 本地开发

本项目现在使用 `uv` 管理 Python 依赖，`uv sync` 以安装依赖。`npm run build` 以构建 `uno.css`，然后 `uvicorn app:app` 即可启动服务。

### Misc | 一些优化

作为一些基于兴趣的编程探索，当时纯手动实现了 SPA 和粗粒度的差量更新，还实现了比较激进的 preloading、PWA 支持和 service worker 等等特性。你可能感觉这个网站（尤其在桌面端）加载特别快，算是一些个人的完美主义吧。

### Roadmap | 以前写的 TODO（不会做了）

- 适配 Open Graph 特性
- 学校视图：左边目录（参考mdn右边），右边正文
- 人物视图：左边头像
- 列表视图：多列布局，头像+姓名
- 预算阅读时间
- 扫描全文，标注所有站内链接
- 首页展示

### Repositories | 项目相关链接

本项目以前托管在 [JihuLab](https://jihulab.com/CNSeniorious000/bnu-history-120) 上，现已迁移至 [GitHub](https://github.com/CNSeniorious000/bnu-history-120)（因为 JihuLab 抛弃免费用户了）。以下是当年处理的一些本站未展示的一些其它来源的数据：

- [bnu-history-parser](https://jihulab.com/CNSeniorious000/bnu-history-parser)
- [bnu-history-parser-2](https://jihulab.com/CNSeniorious000/bnu-history-parser-2)
