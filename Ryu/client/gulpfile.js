const gulp = require('gulp');
const babel = require('gulp-babel');
const uglifycss = require('gulp-uglifycss');
const htmlmin = require('gulp-htmlmin');
const uglify = require('gulp-uglify');

const ARG_MAP = {
    'prod': 'dist',
    'dev': 'build',
}

// Copy vendor file from src to build
gulp.task('vendors', function(){
    let working_folder = getWorkingFolder();
    return gulp.src(['src/vendors/**/*']).pipe(gulp.dest(`${working_folder}/static/vendors`));
});

// copy images from src to build
gulp.task('images', function(){
    let working_folder = getWorkingFolder();
    return gulp.src(['src/images/*']).pipe(gulp.dest(`${working_folder}/static/images`));
});

gulp.task('css', function () {
    let working_folder = getWorkingFolder();
    return gulp.src('src/css/*.css')
        .pipe(uglifycss({
        "uglyComments": true
    }))
    .pipe(gulp.dest(`${working_folder}/static/css/`));
});

gulp.task('js', function () {
    let working_folder = getWorkingFolder();
    return gulp.src('src/js/*.js')
      .pipe(babel({
        presets: ['@babel/env']
      }))
      .pipe(uglify())
      .pipe(gulp.dest(`${working_folder}/static/js/`));
});


gulp.task('html', () => {
    let working_folder = getWorkingFolder();
    return gulp.src('src/templates/*.html')
    .pipe(htmlmin({ collapseWhitespace: true }))
    .pipe(gulp.dest(`${working_folder}/templates/`));
});


gulp.task('run', gulp.series(['html', 'css', 'js']));
gulp.task('watch', function() {
    gulp.watch('src/css/*.css', gulp.series(['css']));
    gulp.watch('src/js/*.js', gulp.series(['js']));
	gulp.watch('src/templates/*.html', gulp.series(['html']));
});
gulp.task('default', gulp.series(['run', 'watch']));


function argumentParser(arg_list) {
    /**
     * Parse command Line arguemnt
     * @param: Command Line argument list
     */

    let arg = {}, a, opt, thisOpt, curOpt;
    for (a = 0; a < arg_list.length; a++) {
        thisOpt = arg_list[a].trim();
        opt = thisOpt.replace(/^\-+/, '');

        if (opt === thisOpt) {
            // argument value
            if (curOpt) arg[curOpt] = opt;
            curOpt = null;
        }
        else {
            // argument name
            curOpt = opt;
            arg[curOpt] = true;
        }
    }
    return arg;
}

function getWorkingFolder() {
    let working_env = argumentParser(process.argv).env || 'dev';
    return ARG_MAP[working_env];
}