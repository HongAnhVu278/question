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


async function drawChart() {
  const data = await d3.json("data/top10_2025.json")

  const usaData = data.entries.find(item => item.code == "USA")

  const usaGirlData = usaData.girls.bars
  const usaBoyData = usaData.boys.bars
  const LABEL = 18

  const x = d3.scaleLinear()
  .domain([0, Math.max(
    d3.max(usaGirlData, d => d.share),
    d3.max(usaBoyData, d => d.share)
  )])
  .range([0,400]);

  const yGirl = d3.scaleBand()
    .domain(usaGirlData.map(d => d.isco))
    .range([0,500])
    .padding(0.2);
  
  const yBoys = d3.scaleBand()
    .domain(usaBoyData.map(d => d.isco))
    .range([0,500])
    .padding(0.2);

  d3.select("#chart-girls")
    .selectAll("rect")
    .data(usaGirlData)
    .join("rect")
    .attr("x", 0)
    .attr("y", d => yGirl(d.isco) + LABEL)
    .attr("width", d => x(d.share))
    .attr("height", yGirl.bandwidth() - LABEL)
    .attr("fill", "tomato")
  
  d3.select("#chart-girls")
    .selectAll("text")
    .data(usaGirlData)
    .join("text")
    .attr("x",0)
    .attr("y", d => yGirl(d.isco)+14)
    .text(d => d.label)
  
  d3.select("#chart-boys")
    .selectAll("rect")
    .data(usaBoyData)
    .join("rect")
    .attr("x", 0)
    .attr("y", d => yBoys(d.isco) +  LABEL)
    .attr("width", d => x(d.share))
    .attr("height", yBoys.bandwidth() - LABEL )
    .attr("fill", "tomato")
  
  d3.select("#chart-boys")
    .selectAll("text")
    .data(usaBoyData)
    .join("text")
    .attr("x",0)
    .attr("y", d => yBoys(d.isco)+14)
    .text(d => d.label)

}

drawChart()

