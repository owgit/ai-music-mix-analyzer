// Matomo Analytics
var _paq = window._paq = window._paq || [];
/* tracker methods like "setCustomDimension" should be called before "trackPageView" */
_paq.push(['trackPageView']);
_paq.push(['enableLinkTracking']);
(function() {
  var u = MATOMO_URL + '/';
  _paq.push(['setTrackerUrl', u + 'matomo.php']);
  _paq.push(['setSiteId', MATOMO_SITE_ID]);
  var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
  g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
})();

// Custom tracking functions
function trackUpload(fileName, fileSize, fileType) {
  _paq.push(['trackEvent', 'Upload', 'Track Upload', `${fileName} (${fileType})`, fileSize]);
}

function trackTabChange(fromTab, toTab) {
  _paq.push(['trackEvent', 'Navigation', 'Tab Change', `${fromTab} to ${toTab}`]);
}

function trackPlayback(trackName, action) {
  _paq.push(['trackEvent', 'Playback', action, trackName]);
}

function trackDownload(trackName) {
  _paq.push(['trackEvent', 'Download', 'Track Download', trackName]);
}

// Mix Analyzer specific tracking functions
function trackAnalysisStart(fileName) {
  _paq.push(['trackEvent', 'Analysis', 'Start Analysis', fileName]);
}

function trackAnalysisComplete(fileName, duration) {
  _paq.push(['trackEvent', 'Analysis', 'Complete Analysis', fileName, duration]);
}

function trackScore(category, score) {
  _paq.push(['trackEvent', 'Scores', category, 'Score Value', score]);
}

function trackVisualization(type, trackName) {
  _paq.push(['trackEvent', 'Visualization', type, trackName]);
}

function trackAIInsight(insightType) {
  _paq.push(['trackEvent', 'AI Insights', 'View', insightType]);
}

// Add event listeners once DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Track tab changes
  const tabElements = document.querySelectorAll('[role="tab"]');
  let currentTab = '';
  
  tabElements.forEach(tab => {
    tab.addEventListener('click', function() {
      const newTab = this.getAttribute('aria-label') || this.textContent;
      if (currentTab !== newTab) {
        trackTabChange(currentTab || 'none', newTab);
        currentTab = newTab;
      }
    });
  });

  // Track file uploads
  const uploadInputs = document.querySelectorAll('input[type="file"]');
  uploadInputs.forEach(input => {
    input.addEventListener('change', function() {
      if (this.files && this.files[0]) {
        const file = this.files[0];
        trackUpload(file.name, file.size, file.type);
        trackAnalysisStart(file.name);
      }
    });
  });

  // Track visualization clicks
  const visualizations = document.querySelectorAll('.visualization-container img');
  visualizations.forEach(viz => {
    viz.addEventListener('click', function() {
      const vizType = this.getAttribute('data-track-name') || 'Unknown';
      trackVisualization('View', vizType);
    });
  });

  // Track scores when they're updated
  const observeScores = () => {
    const scoreElements = {
      'Overall': document.getElementById('overall-score'),
      'Frequency': document.getElementById('frequency-score'),
      'Dynamics': document.getElementById('dynamics-score'),
      'Width': document.getElementById('width-score'),
      'Phase': document.getElementById('phase-score'),
      'Clarity': document.getElementById('clarity-score'),
      'Transients': document.getElementById('transients-score')
    };

    for (const [category, element] of Object.entries(scoreElements)) {
      if (element && element.textContent !== '0') {
        trackScore(category, parseFloat(element.textContent));
      }
    }
  };

  // Track AI Insights view
  const aiTab = document.querySelector('[data-tab="ai-insights"]');
  if (aiTab) {
    aiTab.addEventListener('click', () => {
      trackAIInsight('View AI Analysis');
    });
  }

  // Track downloads
  const downloadLinks = document.querySelectorAll('[data-track-download]');
  downloadLinks.forEach(link => {
    link.addEventListener('click', function() {
      const trackName = this.getAttribute('data-track-download') || this.getAttribute('download') || 'Unknown Track';
      trackDownload(trackName);
    });
  });

  // Observe score changes
  const observer = new MutationObserver(observeScores);
  const scoreElements = document.querySelectorAll('.score-value');
  scoreElements.forEach(element => {
    observer.observe(element, { childList: true, characterData: true, subtree: true });
  });
}); 