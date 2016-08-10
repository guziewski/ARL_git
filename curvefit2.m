clear all;
close all;
x=[0 .005 .01 .015 .02 .025];
y=[0 0.0106646362531 0.0197847446341 0.0440064935907 0.0877602869191 0.13183857967]*100;
A=[.05 50];
x=x*1.60217662e-28/10.9e-30
fun=@(A) curvefit(x,y,A);
B=fminsearch(fun,A)
n=0;
for i=0:x(length(x))/20:x(length(x))
    n=n+1;
    xplot(n)=i;
    v(n)=B(1)*exp(B(2)*i)-B(1);
end

scatter(x,y,'r')
hold on
plot(xplot,v)

m=B(1)*B(2)