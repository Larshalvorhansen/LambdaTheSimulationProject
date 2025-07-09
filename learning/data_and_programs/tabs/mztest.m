function [c,beta,p_value] = mztest(y,x)
mdl=fitlm(x,y);
Variables=mdl.Coefficients.Variables;
c=Variables(1,1);
beta=Variables(2,1);
p_value=coefTest(mdl,[1 0; 0 1],[0 1]);
end

