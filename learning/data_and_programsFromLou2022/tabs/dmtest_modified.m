function [DM,p_value] = dmtest_modified(e1, e2, h)
%DMTEST: Retrieves the Diebold-Mariano test statistic (1995) for the 
% equality of forecast accuracy of two forecasts under general assumptions.
%
%   DM = dmtest(e1, e2, ...) calculates the D-M test statistic on the base 
%   of the loss differential which is defined as the difference of the 
%   squared forecast errors
%
%   In particular, with the DM statistic one can test the null hypothesis: 
%   H0: E(d) = 0. The Diebold-Mariano test assumes that the loss 
%   differential process 'd' is stationary and defines the statistic as:
%   DM = mean(d) / sqrt[ (1/T) * VAR(d) ]  ~ N(0,1),
%   where VAR(d) is an estimate of the unconditional variance of 'd'.
%
%   This function also corrects for the autocorrelation that multi-period 
%   forecast errors usually exhibit. Note that an efficient h-period 
%   forecast will have forecast errors following MA(h-1) processes. 
%   Diebold-Mariano use a Newey-West type estimator for sample variance of
%   the loss differential to account for this concern.
%
%   'e1' is a 'T1-by-1' vector of the forecast errors from the first model
%   'e2' is a 'T2-by-1' vector of the forecast errors from the second model
%
%   It should hold that T1 = T2 = T.
%
%   DM = DMTEST(e1, e2, 'h') allows you to specify an additional parameter 
%   value 'h' to account for the autocorrelation in the loss differential 
%   for multi-period ahead forecasts.   
%       'h'         the forecast horizon, initially set equal to 1
%
%   DM = DMTEST(...) returns a constant:
%       'DM'      the Diebold-Mariano (1995) test statistic
%
%  Semin Ibisevic (2011)
%  $Date: 11/29/2011 $
%
% -------------------------------------------------------------------------
% References
% K. Bouman. Quantitative methods in international finance and 
% macroeconomics. Econometric Institute, 2011. Lecture FEM21004-11.
% 
% Diebold, F.X. and R.S. Mariano (1995), "Comparing predictive accuracy", 
% Journal of Business & Economic Statistics, 13, 253-263.
% -------------------------------------------------------------------------

if nargin < 2
    error('dmtest:TooFewInputs','At least two arguments are required');
end
if nargin < 3
   h = 1; 
end
if size(e1,1) ~= size(e2,1) || size(e1,2) ~= size(e2,2)
    error('dmtest:InvalidInput','Vectors should be of equal length');
end
if size(e1,2) > 1 || size(e2,2) > 1
    error('dmtest:InvalidInput','Input should have T rows and 1 column');
end

% Initialization
n = size(e1,1);

% Define the loss differential
d = abs(e1).^2 - abs(e2).^2;

% Ralculate the variance of the loss differential, taking into account autocorrelation.
if h > 1
    gamma=xcov(d,h-1,'none')/n;
    varD=gamma(h)+2*sum(gamma(1:h-1));
else
    varD=xcov(d,0,'none')/n;
end

% Deal with a negative long-run variance estimate by replacing it with the corresponding short-run variance estimate
if varD<0
    h=1;
    varD=xcov(d,0,'none')/n;
end

% k is calculated to adjuste the statistic as per Harvey, Leybourne, and Newbold (1997) 
k = ((n+1-2*h+(((h)*(h-1))/n))/n)^(1/2);

% Retrieve the diebold mariano statistic DM ~N(0,1)
DM = (mean(d) / sqrt ( (varD/n) ))*k;

% P_VALUE is calculated    
p_value = 2*tcdf(-abs(DM),n-1);
% p_value = tcdf(DM,n-1,'upper');
% p_value = tcdf(DM,n-1);
end

