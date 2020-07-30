const gulp = require('gulp');
const babel = require('gulp-babel');
const uglifycss = require('gulp-uglifycss');
const htmlmin = require('gulp-htmlmin');
const uglify = require('gulp-uglify');

// Copy vendor file from src to build
gulp.task('vendors', function(){
    return gulp.src(['src/vendors/**/*']).pipe(gulp.dest('build/static/vendors'));
});

// copy images from src to build
gulp.task('images', function(){
    return gulp.src(['src/images/*']).pipe(gulp.dest('build/static/images'));
});

gulp.task('css', function () {
    return gulp.src('src/css/*.css')
        .pipe(uglifycss({
        "uglyComments": true
    }))
    .pipe(gulp.dest('build/static/css/'));
});

gulp.task('js', function () {
    return gulp.src('src/js/*.js')
      .pipe(babel({
        presets: ['@babel/env']
      }))
      .pipe(uglify())
      .pipe(gulp.dest('build/static/js/'));
});


gulp.task('html', () => {
    return gulp.src('src/templates/*.html')
    .pipe(htmlmin({ collapseWhitespace: true }))
    .pipe(gulp.dest('build/templates/'));
});


gulp.task('run', gulp.series(['html', 'css', 'js']));
gulp.task('watch', function() {
    gulp.watch('src/css/*.css', gulp.series(['css']));
    gulp.watch('src/js/*.js', gulp.series(['js']));
	gulp.watch('src/templates/*.html', gulp.series(['html']));
});
gulp.task('default', gulp.series(['run', 'watch']));