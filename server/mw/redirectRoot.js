// Redirect "/" -> "/dashboard" w/ caching disabled
module.exports = function redirectRoot() {
    return (req, res, next) => {
        if (req.path === "/" || req.path === "") {
            res.set("Cache-Control", "no-store");
            return res.redirect(302, "/dashboard");
        }
        next();
    };
};
