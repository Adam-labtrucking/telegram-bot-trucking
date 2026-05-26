import {interpolate, spring, useCurrentFrame, useVideoConfig, z} from 'remotion';

export const verticalVideoSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  accentColor: z.string(),
});

type VerticalVideoProps = z.infer<typeof verticalVideoSchema>;

export const VerticalStarter: React.FC<VerticalVideoProps> = ({
  title,
  subtitle,
  accentColor,
}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  const headingScale = spring({
    fps,
    frame,
    config: {
      damping: 200,
    },
  });

  const subtitleOpacity = interpolate(frame, [20, 50, durationInFrames - 30], [0, 1, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const progressWidth = interpolate(frame, [0, durationInFrames], [0, 100]);

  return (
    <div
      style={{
        flex: 1,
        background: 'radial-gradient(circle at 20% 20%, #0f172a, #020617)',
        color: 'white',
        fontFamily: 'Inter, system-ui, sans-serif',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: 96,
      }}
    >
      <div />

      <div>
        <div
          style={{
            color: accentColor,
            letterSpacing: 6,
            textTransform: 'uppercase',
            fontSize: 38,
            marginBottom: 30,
          }}
        >
          Trucking Brief
        </div>
        <h1
          style={{
            fontSize: 120,
            lineHeight: 1,
            margin: 0,
            transform: `scale(${headingScale})`,
            transformOrigin: 'left center',
          }}
        >
          {title}
        </h1>
        <p
          style={{
            marginTop: 44,
            maxWidth: 780,
            fontSize: 56,
            lineHeight: 1.2,
            opacity: subtitleOpacity,
          }}
        >
          {subtitle}
        </p>
      </div>

      <div>
        <div
          style={{
            width: '100%',
            height: 18,
            borderRadius: 999,
            backgroundColor: 'rgba(255,255,255,0.2)',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${progressWidth}%`,
              height: '100%',
              backgroundColor: accentColor,
            }}
          />
        </div>
      </div>
    </div>
  );
};
