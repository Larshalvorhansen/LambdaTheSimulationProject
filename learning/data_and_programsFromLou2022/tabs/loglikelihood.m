function [logL, AICtest, BICtest, lagAIC, lagBIC] = loglikelihood(rate0)
nARmax=3;
presample=3;
logL=zeros(nARmax,1);
AICtest=zeros(nARmax,1);
BICtest=zeros(nARmax,1);
for i=1:nARmax
    Y0=rate0(1:presample,:);
    rate0=rate0(presample+1:end,:);
    mod=varm(size(rate0,2),i);
    [Spec,~,logL(i)]=estimate(mod,rate0,'Y0',Y0);
    summary=summarize(Spec);
    AICtest(i)=summary.AIC;
    BICtest(i)=summary.BIC;
end
lagBIC=find(BICtest==min(BICtest));
lagAIC=find(AICtest==min(AICtest));
