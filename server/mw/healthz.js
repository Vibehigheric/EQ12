module.exports = function healthz(extra = {}) {
    return (req, res) => {
        res.set("Cache-Control", "no-store");
        res.json({
            ok: true,
            ts: Date.now(),
            service: "eq12-dashboard",
            version: process.env.EQ12_VERSION || "1.0.0",
            ...extra
        });
    };
};
