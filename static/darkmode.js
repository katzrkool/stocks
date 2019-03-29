function triggerDarkMode(on, set=true) {
    if (set) {
        localStorage.setItem('darkmode',  on.toString())
    }
    if (document.body.classList.contains('darkmode')) {
        document.body.classList.remove('darkmode');
    } else {
        document.body.classList.add('darkmode');
    }
}

function toggle() {
    const darkValue = localStorage.getItem('darkmode');
    if (darkValue === 'true') {
      triggerDarkMode(false);
    } else {
        triggerDarkMode(true);
    }
}

function darkTest(e) {
    if (e.matches) {
        triggerDarkMode(true);
    } else {
        triggerDarkMode(false);
    }
}

function init() {
    const darkValue = localStorage.getItem('darkmode');
    const mql = window.matchMedia('(prefers-color-scheme: dark)');
    mql.addListener(darkTest);

    // Some of the things in the statements below are redundant, but I really want to make sure someone's preference
    // doesn't get messed up.
    if (darkValue) {
        if (darkValue === 'true') {
            triggerDarkMode(true);
        } else if (darkValue === 'false') {
            triggerDarkMode(false);
        }
    } else {
        if (mql.matches) {
            triggerDarkMode(true, false);
        } else {
            triggerDarkMode(false, false);
        }
    }
}

init();