function error=curvefit(x,y,A)
L=length(x);
error=0;
for i=1:L
    v=A(1)*exp(A(2)*x(i))-A(1);
    error=error+(v-y(i))^2
end
end