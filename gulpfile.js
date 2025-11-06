const gulp = require('gulp');
const sass = require('gulp-sass')(require('sass'));
const autoprefixer = require('gulp-autoprefixer');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const concat = require('gulp-concat');
const rename = require('gulp-rename');
const browserSync = require('browser-sync').create();
const { deleteAsync } = require('del');

// Paths
const paths = {
    scss: {
        src: 'static/velzon/scss/**/*.scss',
        dest: 'static/velzon/css/'
    },
    js: {
        src: 'static/velzon/js/**/*.js',
        dest: 'static/velzon/js/dist/'
    },
    css: {
        src: 'static/velzon/css/**/*.css',
        dest: 'staticfiles/velzon/css/'
    },
    static: {
        src: 'static/velzon/**/*',
        dest: 'staticfiles/velzon/'
    }
};

// Clean task
function clean() {
    return deleteAsync(['staticfiles/velzon/']);
}

// SCSS compilation task
function compileSCSS() {
    return gulp.src(paths.scss.src)
        .pipe(sass({
            outputStyle: 'expanded',
            includePaths: ['node_modules']
        }).on('error', sass.logError))
        .pipe(autoprefixer({
            cascade: false
        }))
        .pipe(gulp.dest(paths.scss.dest))
        .pipe(cleanCSS())
        .pipe(rename({ suffix: '.min' }))
        .pipe(gulp.dest(paths.scss.dest))
        .pipe(browserSync.stream());
}

// JavaScript minification task
function minifyJS() {
    return gulp.src([paths.js.src, '!static/velzon/js/**/*.min.js'])
        .pipe(uglify())
        .pipe(rename({ suffix: '.min' }))
        .pipe(gulp.dest(paths.js.dest));
}

// Copy static files task
function copyStatic() {
    return gulp.src(paths.static.src)
        .pipe(gulp.dest(paths.static.dest));
}

// Watch task
function watchFiles() {
    gulp.watch(paths.scss.src, compileSCSS);
    gulp.watch(paths.js.src, minifyJS);
    gulp.watch('templates/**/*.html').on('change', browserSync.reload);
}

// Browser sync task
function browserSyncInit() {
    browserSync.init({
        proxy: 'localhost:8000',
        port: 3000,
        open: false,
        notify: false
    });
}

// Development task
const dev = gulp.series(clean, gulp.parallel(compileSCSS, minifyJS), gulp.parallel(watchFiles, browserSyncInit));

// Build task
const build = gulp.series(clean, gulp.parallel(compileSCSS, minifyJS, copyStatic));

// Default task
const defaultTask = gulp.series(compileSCSS);

// Export tasks
exports.clean = clean;
exports.sass = compileSCSS;
exports.js = minifyJS;
exports.copy = copyStatic;
exports.watch = watchFiles;
exports.dev = dev;
exports.build = build;
exports.default = defaultTask;