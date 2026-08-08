function sendEnquiry(e){
  e.preventDefault();
  var biz = document.getElementById('biz').value.trim();
  var town = document.getElementById('town').value.trim();
  var email = document.getElementById('email').value.trim();
  var subject = encodeURIComponent('Free sample website request — ' + biz);
  var body = encodeURIComponent(
    'Business: ' + biz + '\n' +
    'Town/suburb: ' + town + '\n' +
    'Email: ' + email + '\n\n' +
    'Please build my free sample website.'
  );
  document.getElementById('formnote').textContent =
    'Opening your email app… if nothing happens, mail lehauthabang@gmail.com directly.';
  window.location.href = 'mailto:lehauthabang@gmail.com?subject=' + subject + '&body=' + body;
  return false;
}

// reveal-on-scroll
document.addEventListener('DOMContentLoaded', function(){
  var els = document.querySelectorAll('.card, .stat, .steps li, .plan');
  els.forEach(function(el){ el.style.opacity = 0; el.style.transform = 'translateY(18px)'; el.style.transition = 'opacity .5s ease, transform .5s ease'; });
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(en.isIntersecting){ en.target.style.opacity = 1; en.target.style.transform = 'none'; io.unobserve(en.target); }
    });
  },{threshold:.12});
  els.forEach(function(el){ io.observe(el); });
});
