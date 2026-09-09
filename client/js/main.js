// wrap every stage's contents in a post-it 
document.querySelectorAll('.stage:not(.bare)').forEach(stage => {
  const note = document.createElement('div');
  note.className = 'note';
  while (stage.firstChild) note.appendChild(stage.firstChild);
  stage.appendChild(note);
});

//activate steps + drive the sticky figure
const steps = document.querySelectorAll('.step');

const stepObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;

    steps.forEach(s => s.classList.remove('on'));
    e.target.classList.add('on');

    const scene = e.target.closest('.scene');
    const cue = Number(e.target.dataset.cue || 0);

    // reveal every element in this scene whose cue has been reached
    scene.querySelectorAll('[data-cue]').forEach(el => {
      if (el.classList.contains('step')) return;
      el.classList.toggle('on', Number(el.dataset.cue) <= cue);
    });

    // swap the chart caption if this step names one
    const slot = scene.querySelector('#chartslot');
    if (slot && e.target.dataset.chart) slot.textContent = e.target.dataset.chart;
  });
}, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });

steps.forEach(s => stepObserver.observe(s));

//the dinosaur / fairy / labor market ladder
const ladder = document.querySelectorAll('#ladderSection .ladder li');
const ladderObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    ladder.forEach((li, i) => setTimeout(() => li.classList.add('on'), i * 900));
    ladderObserver.disconnect();
  });
}, { threshold: 0.5 });

if (ladder.length) ladderObserver.observe(document.getElementById('ladderSection'));
