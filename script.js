function sendEnquiry(e){
  e.preventDefault();
  var biz=document.getElementById('biz').value.trim(),
      town=document.getElementById('town').value.trim(),
      email=document.getElementById('email').value.trim(),
      msg=document.getElementById('msg').value.trim();
  var subject=encodeURIComponent('Free sample website request - '+biz);
  var body=encodeURIComponent('Business: '+biz+'\nTown/suburb: '+town+'\nEmail: '+email+'\n\nMessage: '+(msg||'(none)')+'\n\nPlease build my free sample website.');
  document.getElementById('formnote').textContent='Opening your email app. If nothing happens, write to lehauthabang@gmail.com.';
  window.location.href='mailto:lehauthabang@gmail.com?subject='+subject+'&body='+body;
  return false;
}
// Signature element: play the listing sequence when it enters view.
document.addEventListener('DOMContentLoaded',function(){
  var el=document.getElementById('listing');
  if(!el) return;
  if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){ el.classList.add('play'); return; }
  var io=new IntersectionObserver(function(en){
    en.forEach(function(x){ if(x.isIntersecting){ x.target.classList.add('play'); io.unobserve(x.target); } });
  },{threshold:.35});
  io.observe(el);
});
