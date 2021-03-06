function  peaks = findPeaks4( Amp, MAX_PEAK, EPS_PEAK, SSF )

%plot(Amp);

%   This version modified from findPeaks.m by P. Moller-Nielson 
%   28.3.03, pm-n. ( see http://www.daimi.au.dk/~pmn/sound/ )

SPECTRUM_SIZE=length(Amp);
%three = Amp(3:SPECTRUM_SIZE-1);
%two = Amp(2:SPECTRUM_SIZE-2);
%four = Amp(4:SPECTRUM_SIZE);
%threetwo = Amp(3:SPECTRUM_SIZE-1) > Amp(2:SPECTRUM_SIZE-2);
%threefour = Amp(3:SPECTRUM_SIZE-1) > Amp(4:SPECTRUM_SIZE);
%test = threetwo .* threefour;
peakAmp = ( Amp(3:SPECTRUM_SIZE-1) > Amp(2:SPECTRUM_SIZE-2) ) .* ...
          ( Amp(3:SPECTRUM_SIZE-1) > Amp(4:SPECTRUM_SIZE) ) .* ...
          Amp(3:SPECTRUM_SIZE-1); %finds all the peaks from 3:SPECTRUM_SIZE and returns the peak amplitudes as peakAmp
      
%plot(peakAmp);

%MAX_PEAK is the maximum number of peaks we will look at
peakPos = zeros( MAX_PEAK, 1);

maxAmp = max( peakAmp );
nPeaks = 0;

%searches for max-peaks
for p = 1 : MAX_PEAK
  [m, b] = max( peakAmp ); %value, position
  if m <= ( EPS_PEAK * maxAmp )
    break;
  end;
  peakPos(p) = b+2; %+2 since peakAmp starts at 3
  peakAmp(b) = 0; %set the Amp at b to 0 since we don't want to consider that peak again
  nPeaks = p; %nPeaks = p since the loop might break before it makes it to MAX_PEAK
end;

peakPos = sort( peakPos );
%plot(peakPos);
peaks = zeros( nPeaks, 3 );

last_b = 1;

for p = 1 : nPeaks
  b = peakPos(MAX_PEAK-nPeaks+p); %if nPeaks<MAX_PEAK, then skip past 0s and go to nonzero
  first_b = last_b+1;
  if p == nPeaks
    last_b = SPECTRUM_SIZE;
  else
    next_b = peakPos(MAX_PEAK-nPeaks+p+1);
    [dummy, rel_min] = min(Amp(b:next_b));
    last_b = b+rel_min-1;
  end;
  peaks(p,1) = first_b;
  peaks(p,2) = b;
  peaks(p,3) = last_b;
end;